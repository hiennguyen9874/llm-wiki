// Part of Jev-Style-0.8B-Decision-v3 (Apache-2.0). Tested against llama.cpp commit
// 441df11f65ea0b6d0c72965aaf70c8241070ddcb (2026-09-23); needs a llama.cpp with qwen35 support and
// llama_context_params.n_outputs_max. Build: sh build_jev_score.sh /path/to/llama.cpp
//
// jev-score: score Jev-Style typed decisions with libllama, reading logits only at slot positions.
//
// Persistent JSON-lines server. Start:
//   jev-score --model model.gguf [--n-ctx 32768] [--n-ubatch 1024] [--ngl 999] [--threads 8]
//                [--flash-attn auto|on|off] [--n-outputs-max 256] [--n-seq-max 17]
// It prints one line {"ready":true,...}. Then each stdin line is one request:
//   {"prefix":[ids], "questions":[{"ids":[ids], "slots":[abs positions], "rows":[token ids]}],
//    "share_prefix":true, "keep_prefix":true}
// Positions in "slots" are absolute in prefix+question ids and must lie inside the question part.
// For every slot the response returns the logits of the requested token ids only:
//   {"results":[{"scores":[[...len(rows)] per slot], "finite":true}], "prefix_reused":false,
//    "n_prefix":N, "timing":{"prefix_ms":..,"question_ms":[..],"total_ms":..}}
//
// Mechanics: only slot positions get batch.logits[i] = 1 (never all-token output). With
// share_prefix the prefix is decoded once into sequence 0 and each question is decoded in
// sequence 1 after llama_memory_seq_cp(0 -> 1) (attention KV cells are shared; the recurrent
// GDN state is copied on write by llama.cpp), then sequence 1 is removed. With keep_prefix the
// prefix stays in sequence 0 and an identical prefix in the next request is reused without
// recomputation (recurrent state cannot be rolled back, so only exact matches are reused).
// share_prefix=false decodes prefix+question from scratch per question (reference path).
// "mode" (default "auto"): with share_prefix, "sequential" = one question at a time as above;
// "batched" = questions k=1..G get sequences k (seq_cp 0 -> k) and ALL their tokens go into one
// llama_decode (groups bounded by --n-seq-max - 1 questions, by free KV cells and by
// --n-outputs-max slots per decode: libllama aborts the process on a larger output request);
// "auto" = "fused" for a single question whose prefix is not cached (one decode of
// prefix+question into sequence 0, prefix not kept), "batched" for several questions.
// {"cmd":"reset"} clears the memory; {"cmd":"quit"} exits.

#include "llama.h"
#include "nlohmann/json.hpp"

#include <algorithm>
#include <chrono>
#include <cmath>
#include <cstdio>
#include <cstring>
#include <iostream>
#include <string>
#include <vector>

using json = nlohmann::json;
using clk = std::chrono::steady_clock;

static double ms_since(clk::time_point t0) {
    return std::chrono::duration<double, std::milli>(clk::now() - t0).count();
}

struct Scorer {
    llama_model * model = nullptr;
    llama_context * ctx = nullptr;
    int n_ctx = 0, n_batch = 0, n_vocab = 0, n_seq_max = 2;
    // Max logits rows one llama_decode may request. libllama GGML_ASSERTs (process abort) when a
    // batch asks for more, so every decode is kept within it: a single question with more slots
    // is rejected with an error, batched groups are split by their total slot count.
    int n_outputs_max = 256;
    std::vector<llama_token> cached_prefix;   // content of sequence 0
    bool cached_valid = false;

    void clear() {
        llama_memory_clear(llama_get_memory(ctx), true);
        cached_prefix.clear();
        cached_valid = false;
    }

    // Decode ids at positions [pos0, pos0+n) into seq; request logits at the given absolute positions.
    // Returns the batch index of every requested position (same order as `want`).
    std::vector<int> decode(const std::vector<llama_token> & ids, int pos0, llama_seq_id seq,
                            const std::vector<int> & want) {
        std::vector<int> idx(want.size(), -1);
        const int n = (int) ids.size();
        if (n == 0) return idx;
        // Chunk by n_batch (only the last chunk can hold slots because slots lie in the question).
        for (int start = 0; start < n; start += n_batch) {
            const int len = std::min(n_batch, n - start);
            llama_batch batch = llama_batch_init(len, 0, 1);
            batch.n_tokens = len;
            for (int j = 0; j < len; ++j) {
                batch.token[j] = ids[start + j];
                batch.pos[j] = pos0 + start + j;
                batch.n_seq_id[j] = 1;
                batch.seq_id[j][0] = seq;
                batch.logits[j] = 0;
            }
            for (size_t w = 0; w < want.size(); ++w) {
                const int rel = want[w] - pos0 - start;
                if (rel >= 0 && rel < len) {
                    batch.logits[rel] = 1;
                    idx[w] = rel;
                }
            }
            const int rc = llama_decode(ctx, batch);
            llama_batch_free(batch);
            if (rc != 0) throw std::runtime_error("llama_decode failed with code " + std::to_string(rc));
            for (size_t w = 0; w < want.size(); ++w) {
                const int rel = want[w] - pos0 - start;
                if ((rel >= 0 && rel < len) && start + len < n) {
                    throw std::runtime_error("slot inside a non-final chunk; question longer than n_batch");
                }
            }
        }
        return idx;
    }

    // Decode several questions at once: question k goes to sequence seqs[k] at positions
    // n_prefix.. . Returns per question the batch indices of its slots.
    std::vector<std::vector<int>> decode_group(const std::vector<std::vector<llama_token>> & ids,
                                               const std::vector<std::vector<int>> & slots,
                                               const std::vector<llama_seq_id> & seqs, int n_prefix) {
        int total = 0;
        for (const auto & v : ids) total += (int) v.size();
        if (total > n_batch) throw std::runtime_error("question group larger than n_batch");
        llama_batch batch = llama_batch_init(total, 0, 1);
        batch.n_tokens = total;
        std::vector<std::vector<int>> idx(ids.size());
        int j = 0;
        for (size_t k = 0; k < ids.size(); ++k) {
            std::vector<int> want = slots[k];
            idx[k].assign(want.size(), -1);
            for (size_t t = 0; t < ids[k].size(); ++t, ++j) {
                batch.token[j] = ids[k][t];
                batch.pos[j] = n_prefix + (int) t;
                batch.n_seq_id[j] = 1;
                batch.seq_id[j][0] = seqs[k];
                batch.logits[j] = 0;
                for (size_t w = 0; w < want.size(); ++w) {
                    if (want[w] == n_prefix + (int) t) { batch.logits[j] = 1; idx[k][w] = j; }
                }
            }
        }
        const int rc = llama_decode(ctx, batch);
        llama_batch_free(batch);
        if (rc != 0) throw std::runtime_error("llama_decode (question group) failed with code " + std::to_string(rc));
        return idx;
    }

    json read_slots(const std::vector<int> & idx, const std::vector<llama_token> & rows, bool & finite) {
        json scores = json::array();
        for (int i : idx) {
            const float * lg = llama_get_logits_ith(ctx, i);
            if (!lg) throw std::runtime_error("no logits at requested slot");
            json r = json::array();
            for (llama_token t : rows) {
                if (t < 0 || t >= n_vocab) throw std::runtime_error("row token id out of range");
                const float v = lg[t];
                if (!std::isfinite(v)) finite = false;
                r.push_back(std::isfinite(v) ? json(v) : json(nullptr));
            }
            scores.push_back(r);
        }
        return scores;
    }

    json handle(const json & req) {
        const auto t_total = clk::now();
        std::vector<llama_token> prefix = req.value("prefix", std::vector<llama_token>{});
        const bool share = req.value("share_prefix", true);
        const bool keep = req.value("keep_prefix", true);
        const json & qs = req.at("questions");
        llama_memory_t mem = llama_get_memory(ctx);
        const int n_prefix = (int) prefix.size();
        json out;
        json results = json::array();
        json q_ms = json::array();
        double prefix_ms = 0.0;
        bool reused = false;

        for (const auto & q : qs) {
            std::vector<llama_token> ids = q.at("ids").get<std::vector<llama_token>>();
            if (n_prefix + (int) ids.size() > n_ctx) {
                throw std::runtime_error("input of " + std::to_string(n_prefix + ids.size()) +
                                         " tokens exceeds n_ctx=" + std::to_string(n_ctx) + "; nothing truncated");
            }
            const std::vector<int> qslots = q.at("slots").get<std::vector<int>>();
            if ((int) qslots.size() > n_outputs_max) {
                throw std::runtime_error("question has " + std::to_string(qslots.size()) + " slots; n_outputs_max=" +
                                         std::to_string(n_outputs_max) + " (restart with a larger --n-outputs-max)");
            }
            for (int s : qslots) {
                if (s < n_prefix || s >= n_prefix + (int) ids.size())
                    throw std::runtime_error("slot position outside the question part");
            }
        }

        if (share && n_prefix > 0 && keep && cached_valid && cached_prefix == prefix) reused = true;
        std::string mode = req.value("mode", std::string("auto"));
        if (mode == "auto") mode = qs.size() > 1 ? "batched" : "fused";
        if (!share) mode = "sequential";
        if (mode == "fused" && (qs.size() != 1 || reused)) mode = qs.size() > 1 ? "batched" : "sequential";
        if (mode == "batched" && n_seq_max < 3) mode = "sequential";
        std::vector<json> res_by_q(qs.size());
        std::vector<double> ms_by_q(qs.size(), 0.0);

        if (mode == "fused") {
            // one decode of prefix + question into sequence 0; the prefix is not kept afterwards
            const auto t0 = clk::now();
            const auto & q = qs[0];
            std::vector<llama_token> all(prefix);
            std::vector<llama_token> ids = q.at("ids").get<std::vector<llama_token>>();
            all.insert(all.end(), ids.begin(), ids.end());
            clear();
            std::vector<int> idx = decode(all, 0, 0, q.at("slots").get<std::vector<int>>());
            bool finite = true;
            json scores = read_slots(idx, q.at("rows").get<std::vector<llama_token>>(), finite);
            clear();
            ms_by_q[0] = ms_since(t0);
            res_by_q[0] = {{"scores", scores}, {"finite", finite}};
        } else {
            if (share && n_prefix > 0 && !reused) {
                const auto t0 = clk::now();
                clear();
                decode(prefix, 0, 0, {});
                llama_synchronize(ctx);
                prefix_ms = ms_since(t0);
                cached_prefix = prefix;
                cached_valid = true;
            }
            size_t i = 0;
            while (i < qs.size()) {
                const auto t0 = clk::now();
                // group: up to n_seq_max-1 questions whose tokens fit the free KV cells and n_batch
                // and whose slots together stay within n_outputs_max (one llama_decode)
                std::vector<size_t> grp;
                int used = 0, outs = 0;
                const int cap = mode == "batched" ? n_seq_max - 1 : 1;
                while (i < qs.size() && (int) grp.size() < cap) {
                    const int len = (int) qs[i].at("ids").size();
                    const int ns = (int) qs[i].at("slots").size();
                    if (!grp.empty() && (n_prefix + used + len > n_ctx || used + len > n_batch ||
                                         outs + ns > n_outputs_max)) break;
                    grp.push_back(i++);
                    used += len;
                    outs += ns;
                }
                std::vector<std::vector<llama_token>> ids;
                std::vector<std::vector<int>> slots;
                std::vector<llama_seq_id> seqs;
                for (size_t k = 0; k < grp.size(); ++k) {
                    const llama_seq_id sq = (llama_seq_id) (k + 1);
                    llama_memory_seq_rm(mem, sq, -1, -1);
                    if (share && n_prefix > 0) llama_memory_seq_cp(mem, 0, sq, -1, -1);
                    ids.push_back(qs[grp[k]].at("ids").get<std::vector<llama_token>>());
                    slots.push_back(qs[grp[k]].at("slots").get<std::vector<int>>());
                    seqs.push_back(sq);
                }
                std::vector<std::vector<int>> idx;
                if (share) {
                    idx = decode_group(ids, slots, seqs, n_prefix);
                } else {    // reference path: prefix + question from scratch
                    clear();
                    std::vector<llama_token> all(prefix);
                    all.insert(all.end(), ids[0].begin(), ids[0].end());
                    idx.push_back(decode(all, 0, 1, slots[0]));
                }
                for (size_t k = 0; k < grp.size(); ++k) {
                    bool finite = true;
                    json scores = read_slots(idx[k], qs[grp[k]].at("rows").get<std::vector<llama_token>>(), finite);
                    res_by_q[grp[k]] = {{"scores", scores}, {"finite", finite}};
                }
                for (auto sq : seqs) llama_memory_seq_rm(mem, sq, -1, -1);
                const double per = ms_since(t0) / (double) grp.size();
                for (size_t k : grp) ms_by_q[k] = per;
            }
        }
        for (size_t k = 0; k < qs.size(); ++k) {
            results.push_back(res_by_q[k]);
            q_ms.push_back(ms_by_q[k]);
        }
        out["mode"] = mode;
        if (!share || !keep) clear();
        out["results"] = results;
        out["prefix_reused"] = reused;
        out["n_prefix"] = n_prefix;
        out["timing"] = {{"prefix_ms", prefix_ms}, {"question_ms", q_ms}, {"total_ms", ms_since(t_total)}};
        return out;
    }
};

static void usage() {
    fprintf(stderr, "usage: jev-score --model PATH [--n-ctx N] [--n-ubatch N] [--ngl N] [--threads N] "
                    "[--flash-attn auto|on|off] [--n-outputs-max N] [--n-seq-max N]\n");
}

int main(int argc, char ** argv) {
    std::string model_path, fa = "auto";
    int n_ctx = 32768, n_ubatch = 1024, ngl = 999, threads = 8, n_out = 256, n_seq = 17;  // 25,600-token context + question room
    for (int i = 1; i < argc; ++i) {
        std::string a = argv[i];
        auto next = [&]() -> std::string {
            if (i + 1 >= argc) { usage(); exit(2); }
            return argv[++i];
        };
        if (a == "--model") model_path = next();
        else if (a == "--n-ctx") n_ctx = std::stoi(next());
        else if (a == "--n-ubatch") n_ubatch = std::stoi(next());
        else if (a == "--ngl") ngl = std::stoi(next());
        else if (a == "--threads") threads = std::stoi(next());
        else if (a == "--flash-attn") fa = next();
        else if (a == "--n-outputs-max") n_out = std::stoi(next());
        else if (a == "--n-seq-max") n_seq = std::stoi(next());
        else { usage(); return 2; }
    }
    if (model_path.empty()) { usage(); return 2; }
    if (n_out < std::max(2, n_seq)) {   // libllama reserves max(n_outputs, n_seq_max) rows and asserts on it
        std::cout << json{{"ready", false}, {"error", "--n-outputs-max must be >= --n-seq-max"}}.dump() << std::endl;
        return 2;
    }

    const auto t0 = clk::now();
    llama_log_set([](enum ggml_log_level level, const char * text, void *) {
        if (level >= GGML_LOG_LEVEL_WARN) fputs(text, stderr);
    }, nullptr);
    llama_backend_init();
    llama_model_params mp = llama_model_default_params();
    mp.n_gpu_layers = ngl;
    Scorer S;
    S.model = llama_model_load_from_file(model_path.c_str(), mp);
    if (!S.model) { std::cout << json{{"ready", false}, {"error", "model load failed"}}.dump() << std::endl; return 1; }
    llama_context_params cp = llama_context_default_params();
    cp.n_ctx = n_ctx;
    cp.n_batch = n_ctx;
    cp.n_ubatch = std::min(n_ubatch, n_ctx);
    cp.n_seq_max = std::max(2, n_seq);
    cp.n_outputs_max = n_out;
    cp.n_threads = threads;
    cp.n_threads_batch = threads;
    cp.kv_unified = true;
    cp.no_perf = true;
    cp.flash_attn_type = fa == "on" ? LLAMA_FLASH_ATTN_TYPE_ENABLED
                       : fa == "off" ? LLAMA_FLASH_ATTN_TYPE_DISABLED : LLAMA_FLASH_ATTN_TYPE_AUTO;
    S.ctx = llama_init_from_model(S.model, cp);
    if (!S.ctx) { std::cout << json{{"ready", false}, {"error", "context init failed"}}.dump() << std::endl; return 1; }
    S.n_ctx = (int) llama_n_ctx(S.ctx);
    S.n_batch = (int) llama_n_batch(S.ctx);
    S.n_seq_max = (int) llama_n_seq_max(S.ctx);
    S.n_outputs_max = (int) cp.n_outputs_max;
    S.n_vocab = llama_vocab_n_tokens(llama_model_get_vocab(S.model));
    char desc[256];
    llama_model_desc(S.model, desc, sizeof(desc));
    std::cout << json{{"ready", true}, {"n_ctx", S.n_ctx}, {"n_batch", S.n_batch}, {"n_ubatch", cp.n_ubatch}, {"n_seq_max", S.n_seq_max}, {"n_outputs_max", S.n_outputs_max},
                      {"n_vocab", S.n_vocab}, {"desc", desc}, {"load_ms", ms_since(t0)},
                      {"system_info", llama_print_system_info()}}.dump() << std::endl;

    std::string line;
    while (std::getline(std::cin, line)) {
        if (line.empty()) continue;
        json resp;
        try {
            json req = json::parse(line);
            const std::string cmd = req.value("cmd", "");
            if (cmd == "quit") break;
            if (cmd == "reset") { S.clear(); resp = {{"ok", true}}; }
            else resp = S.handle(req);
        } catch (const std::exception & e) {
            try { S.clear(); } catch (...) {}
            resp = {{"error", e.what()}};
        }
        std::cout << resp.dump() << std::endl;
    }
    llama_free(S.ctx);
    llama_model_free(S.model);
    llama_backend_free();
    return 0;
}
