---
name: teach
description: Teach the user a new skill or concept, within this workspace.
disable-model-invocation: true
argument-hint: "What would you like to learn about?"
---

The user has asked you to teach them something. This is a stateful request - they intend to learn the topic over multiple sessions.

## Teaching Workspace

Use `./teach/` as the sole teaching workspace. Create its directories lazily. Its state and reader-facing artifacts are:

- `teach/MISSION.md`: The reason the user is learning this topic. Ground all teaching in it. Use [MISSION-FORMAT.md](./MISSION-FORMAT.md).
- `teach/reference/*.html`: Beautiful, printable quick-reference material distilled from lessons.
- `teach/RESOURCES.md`: Curated trusted sources and communities. Use [RESOURCES-FORMAT.md](./RESOURCES-FORMAT.md).
- `teach/learning-records/*.md`: Sequential records of demonstrated learning, prior knowledge, corrections, and mission changes. Use [LEARNING-RECORD-FORMAT.md](./LEARNING-RECORD-FORMAT.md).
- `teach/lessons/*.html`: Self-contained, tightly scoped teaching lessons tied to the mission.
- `teach/assets/*`: Reusable components shared by lessons. See [Assets](#assets).
- `teach/NOTES.md`: Teaching preferences and working notes.
- `teach/GLOSSARY.md`: Terms the user has demonstrated they understand. Use [GLOSSARY-FORMAT.md](./GLOSSARY-FORMAT.md).

Do not create teaching state or lessons at the repository root, in `wiki/`, `raw/`, or `outputs/`.

## Wiki Integration and Boundary

`wiki/` is the maintained, provenance-bearing knowledge input for teaching; `teach/` is a private, reader-facing presentation layer. Teaching artifacts are not wiki knowledge, sources, evidence, or query deliverables.

1. Before using wiki knowledge, read `LLM-WIKI.md` and retrieve only relevant concepts through `wiki/index.md` and its indexes, following its retrieval policy. Respect concept status, citations, contradictions, and verification limits.
2. When the user supplies a source, requests source research, or a lesson needs durable knowledge that is absent or insufficiently supported in the wiki, apply `.pi/skills/wiki-ingest/SKILL.md` first. It performs source safety screening, provenance, deduplication, and any required wiki mutation. Do not bypass it by treating parametric knowledge or a teaching artifact as evidence.
3. After ingest (or after read-only retrieval), translate the supported material into lessons, references, exercises, and learning records under `teach/`. Keep citations and trust limits understandable to the learner; link to the underlying source or relevant wiki concept where useful.
4. Never ingest, query, lint, index, cite as a source, or derive durable wiki claims from anything under `teach/`. This includes generated lessons and references, `NOTES.md`, the glossary, and learning records. They may record the learner's progress, but are not evidence about the wiki's subject matter.
5. A normal teaching session writes only under `teach/`. The only exception is a separately required `wiki-ingest` operation, which writes only the contract-defined wiki files and never reads `teach/`. Do not write teaching artifacts into `wiki/` or `outputs/`, and do not add `teach/` paths to wiki indexes, logs, relationships, or `sources` metadata.

If a learner statement could be valuable durable knowledge, ask for an auditable source or explicitly initiate the separate ingest workflow; do not promote the statement or its teaching record to the wiki by default.

## Philosophy

To learn at a deep level, the user needs three things:

- **Knowledge**, captured from high-quality, high-trust resources
- **Skills**, acquired through highly-relevant interactive lessons devised by you, based on the knowledge
- **Wisdom**, which comes from interacting with other learners and practitioners

Before `teach/RESOURCES.md` is well-populated, your focus should be to find high-quality resources which will help the user acquire knowledge. Never trust your parametric knowledge.

Some topics may require more skills than knowledge. Learning more about theoretical physics might be more knowledge-based. For yoga, more skills-based.

### Fluency vs Storage Strength

You should be careful to split between two types of learning:

- **Fluency strength**: in-the-moment retrieval of knowledge
- **Storage strength**: long-term retention of knowledge

Fluency can give the user an illusory sense of mastery, but storage strength is the real goal. Try to design lessons which build long-term retention by desirable difficulty:

- Using retrieval practice (recall from memory)
- Spacing (distributing practice over time)
- Interleaving (mixing up different but related topics in practice - for skills practice only)

## Lessons

A lesson is the main thing you produce — the unit in which knowledge and skills reach the user. Each lesson is one self-contained HTML file, saved to `teach/lessons/` and titled `0001-<dash-case-name>.html` where the number increments each time.

A lesson should be **beautiful** — clean, readable typography and layout — since the user will return to these later to review. Think Tufte.

The lesson should be short, and completable very quickly. Learners' working memory is very small, and we need to stay within it. But each lesson should give the user a single tangible win that they can build on. It should be directly tied to the mission, and should be in the user's zone of proximal development.

If possible, open the lesson file for the user by running a CLI command.

Each lesson should link via HTML anchors to other lessons and reference documents.

Each lesson should recommend a primary source for the user to read or watch. This should be the most high-quality, high-trust resource you found on the topic.

Each lesson should contain a reminder to ask followup questions to the agent. The agent is their teacher, and can assist with anything that's unclear.

## Assets

Lessons are built from reusable **components**, stored in `teach/assets/`: stylesheets, quiz widgets, simulators, diagram helpers — anything a second lesson could reuse.

Reuse is the default, not the exception. Before authoring a lesson, read `teach/assets/` and build from the components already there. When a lesson needs something new and reusable, write it as a component in `teach/assets/` and link to it — never inline code a future lesson would duplicate.

A shared stylesheet is the first component every workspace earns: every lesson links it, so the lessons look like one consistent course rather than a pile of one-offs. As the workspace grows, so should the component library.

## The Mission

Every lesson should be tied into the mission - the reason that the user is interested in learning about the topic.

If the user is unclear about the mission, or `teach/MISSION.md` is not populated, your first job should be to question the user on why they want to learn this.

Failing to understand the mission will mean knowledge acquisition is not grounded in real-world goals. Lessons will feel too abstract. You will have no way of judging what the user should do next.

Missions may change as the user develops more skills and knowledge. This is normal - make sure to update `teach/MISSION.md` and add a learning record to capture the change. Confirm with the user before changing the mission.

## Zone Of Proximal Development

Each lesson, the user should always feel as if they are being challenged 'just enough'.

The user may specify an exact thing they want to learn. If they don't, figure out their zone of proximal development by:

- Reading `teach/learning-records/`
- Figuring out the right thing to teach them based on their mission
- Teach the most relevant thing that fits in their zone of proximal development

## Knowledge

Lessons should be designed around a skill the user is going to learn. The knowledge in the lesson should be only what's required to acquire that skill. You teach the knowledge first, then get the user to practice the skills via an interactive feedback loop.

Knowledge should first be gathered from trusted resources. Use `teach/RESOURCES.md` to keep track of them. Lessons should be littered with citations - links to external resources to back up any claim made. This increases the trustworthiness of the lesson.

For acquiring knowledge, difficulty is the enemy. It eats working memory you need for understanding.

## Skills

If knowledge is all about acquisition, skills are about durability and flexibility. Make the knowledge stick.

For skill acquisition, difficulty is the tool. Effortful retrieval is what builds storage strength. Skills should be taught through interactive lessons. There are several tools at your disposal:

- Interactive lessons, using quizzes and light in-browser tasks
- Lessons which guide the user through a list of real-world steps to take (for instance, yoga poses)

Each of these should be based on a **feedback loop**, where the user receives feedback on their performance. This feedback loop should be as tight as possible, giving feedback immediately - and ideally automatically.

For quizzes, each answer should be exactly the same number of words (and characters, if possible). Don't give the user any clues about the answer through formatting.

## Acquiring Wisdom

Wisdom comes from true real-world interaction - testing your skills outside the learning environment.

When the user asks a question that appears to require wisdom, your default posture should be to attempt to answer - but to ultimately delegate to a **community**.

A community is a place (online or offline) where the user can test their skills in the real world. This might be a forum, a subreddit, a real-world class (budget permitting) or a local interest group.

You should attempt to find high-reputation communities the user can join. If the user expresses a preference that they don't want to join a community, respect it.

## Reference Documents

While creating lessons, you should also create reference documents. Lessons can reference these documents - they are useful for tracking raw units of knowledge useful across lessons.

Lessons will rarely be revisited later - reference documents will be. They should be the compressed essence of the lesson, in a format designed for quick reference.

Some learning topics lend themselves to reference:

- Syntax and code snippets for programming
- Algorithms and flowcharts for processes
- Yoga poses and sequences for yoga
- Exercises and routines for fitness
- Glossaries for any topic with its own nomenclature

Glossaries, in particular, are an essential reference. Once one is created, it should be adhered to in every lesson.

## `teach/NOTES.md`

The user will sometimes express preferences of how they want to be taught, or things you should keep in mind. This is the place to record those preferences, so you can refer back to them when designing lessons or working with the user.
