// Mineflayer skill server for minecraft.py: the NLI model picks a skill, this process executes it in a real Minecraft world.
//   node mc_bot.js [--port 25570] [--http 3007]
//   GET  /state                      -> inventory / stations / visible blocks
//   POST /act   {skill, arg, n}      -> {ok, msg}   skills: collect | craft | place | smelt | explore
//   POST /reset {x, z}               -> clear inventory, teleport to a fresh spot
const mineflayer = require('mineflayer')
const { pathfinder, Movements, goals } = require('mineflayer-pathfinder')
const { Vec3 } = require('vec3')
const http = require('http')

const argv = process.argv.slice(2)
const opt = (k, d) => { const i = argv.indexOf(k); return i >= 0 ? argv[i + 1] : d }
const bot = mineflayer.createBot({ host: '127.0.0.1', port: +opt('--port', 25570), username: opt('--name', 'jev'), version: '1.20.4' })
bot.loadPlugin(pathfinder)
let mcData, ready = false
const sleep = ms => new Promise(r => setTimeout(r, ms))

// text-level groups: the planner only ever sees these names
const BLOCKS = { log: n => n.endsWith('_log') && !n.startsWith('stripped'), stone: n => n === 'stone', iron_ore: n => n === 'iron_ore' || n === 'deepslate_iron_ore' }
const ITEMS = { log: n => n.endsWith('_log'), planks: n => n.endsWith('_planks'), stick: n => n === 'stick', cobblestone: n => n === 'cobblestone' }
const DROPS = { log: 'log', stone: 'cobblestone', iron_ore: 'raw_iron' }
const RADIUS = { log: 48, stone: 32, iron_ore: 64 }
const itemMatch = g => ITEMS[g] || (n => n === g)
const count = g => bot.inventory.items().filter(i => itemMatch(g)(i.name)).reduce((s, i) => s + i.count, 0)
const blockIds = g => Object.values(mcData.blocksByName).filter(b => BLOCKS[g](b.name)).map(b => b.id)
const bad = new Set()

bot.once('spawn', async () => {
  mcData = require('minecraft-data')(bot.version)
  const mv = new Movements(bot)
  mv.allow1by1towers = true; mv.canDig = true; mv.allowParkour = true
  bot.pathfinder.setMovements(mv)
  bot.pathfinder.thinkTimeout = 10000
  for (const c of ['gamerule doDaylightCycle false', 'time set day', 'gamerule doWeatherCycle false', 'weather clear', 'gamerule keepInventory true', 'difficulty peaceful']) { bot.chat('/' + c); await sleep(150) }
  if (opt('--viewer', null)) require('prismarine-viewer').mineflayer(bot, { port: +opt('--viewer'), firstPerson: opt('--view', 'first') === 'first', viewDistance: 5 })
  ready = true
  console.log('bot ready at', bot.entity.position.floored().toString())
})
bot.on('kicked', r => console.log('kicked', r))
bot.on('error', e => console.log('error', e.message))
bot.on('death', () => console.log('bot died'))

function findNear(g) {
  const pos = bot.findBlocks({ matching: blockIds(g), maxDistance: RADIUS[g], count: 64 }).filter(p => !bad.has(p.toString()))
  const me = bot.entity.position
  // prefer exposed blocks that are not high above the head (tree tops need towers, buried blocks need tunnels)
  const exposed = p => [[1, 0, 0], [-1, 0, 0], [0, 1, 0], [0, 0, 1], [0, 0, -1]].some(d => { const b = bot.blockAt(p.offset(...d)); return b && b.name === 'air' })
  const cost = p => p.distanceTo(me) + 4 * Math.max(0, p.y - me.y - 3) + (p.distanceTo(me) < 24 && !exposed(p) ? 10 : 0)
  return pos.map(p => [cost(p), p]).sort((a, b) => a[0] - b[0]).map(x => x[1])
}
const station = name => bot.findBlock({ matching: mcData.blocksByName[name].id, maxDistance: 32 })

function state() {
  const inv = {}
  for (const i of bot.inventory.items()) {
    const g = Object.keys(ITEMS).find(k => ITEMS[k](i.name)) || i.name
    inv[g] = (inv[g] || 0) + i.count
  }
  const p = bot.entity.position
  return {
    inventory: inv, pos: [Math.round(p.x), Math.round(p.y), Math.round(p.z)], health: bot.health,
    near: { crafting_table: !!station('crafting_table'), furnace: !!station('furnace') },
    visible: Object.fromEntries(Object.keys(BLOCKS).map(g => [g, findNear(g).length > 0]))
  }
}

async function withTimeout(p, ms, what) {
  let t
  // stop() with no active path would cancel the *next* goto, so only clean up after a real timeout
  const timer = new Promise((_, rej) => { t = setTimeout(() => { bot.pathfinder.setGoal(null); try { bot.stopDigging() } catch (e) {} ; rej(new Error(`timeout: ${what}`)) }, ms) })
  try { return await Promise.race([p, timer]) } finally { clearTimeout(t) }
}

async function pickupNear(pos) {
  await sleep(350)
  for (let k = 0; k < 3; k++) {
    const e = Object.values(bot.entities).filter(e => e.name === 'item' && e.position.distanceTo(pos) < 6).sort((a, b) => a.position.distanceTo(bot.entity.position) - b.position.distanceTo(bot.entity.position))[0]
    if (!e) return
    try { await withTimeout(bot.pathfinder.goto(new goals.GoalNear(e.position.x, e.position.y, e.position.z, 0.7)), 15000, 'pickup') } catch (err) { return }
    await sleep(300)
  }
}

async function collect(g, n) {
  if (!BLOCKS[g]) return { ok: false, msg: `unknown block group ${g}` }
  const drop = DROPS[g], start = count(drop)
  for (let tries = 0; count(drop) < start + n && tries < n * 3 + 4; tries++) {
    const cands = findNear(g)
    if (!cands.length) break
    const block = bot.blockAt(cands[0])
    try {
      await withTimeout(bot.pathfinder.goto(new goals.GoalNear(block.position.x, block.position.y, block.position.z, 3)), 60000, 'path to ' + g)
      if (!bot.canDigBlock(block)) throw new Error('block out of reach')
      const tool = bot.pathfinder.bestHarvestTool(block)
      if (tool) await bot.equip(tool, 'hand')
      if (!block.canHarvest(bot.heldItem ? bot.heldItem.type : null)) return { ok: false, msg: `cannot harvest ${g} without a suitable pickaxe` }
      await withTimeout(bot.dig(block), 30000, 'dig ' + g)
      await pickupNear(block.position)
    } catch (e) { bad.add(cands[0].toString()); console.log('collect err', e.message) }
  }
  const got = count(drop) - start
  return got > 0 ? { ok: true, msg: `collected ${got} ${drop}` } : { ok: false, msg: `no reachable ${g} block found nearby` }
}

// bot.craft() clicks the next ingredient while the previous one is still on the cursor (swap -> garbage in the grid),
// so the clicks are done here: pick a stack, right-click one item into each grid slot, put the rest back, take the result.
async function craftOnce(recipe, table) {
  const win = recipe.requiresTable ? await bot.openBlock(table) : bot.inventory, w = recipe.requiresTable ? 3 : 2
  const click = async (slot, btn) => { await bot.clickWindow(slot, btn, 0); await sleep(60) }
  try {
    const dests = {}
    if (recipe.inShape) recipe.inShape.forEach((row, y) => row.forEach((ing, x) => { if (ing.id !== -1) (dests[ing.id] = dests[ing.id] || []).push(1 + x + w * y) }))
    else recipe.ingredients.forEach((ing, k) => (dests[ing.id] = dests[ing.id] || []).push(1 + k))
    for (const [id, slots] of Object.entries(dests)) {
      let from = null
      for (const d of slots) {
        if (!win.selectedItem) {  // stacks may be fragmented (4 + 4 + 2 planks): take the next one when the cursor runs empty
          const src = win.findInventoryItem(+id, null)
          if (!src) throw new Error('missing ingredient')
          from = src.slot
          await click(from, 0)
        }
        await click(d, 1)
      }
      if (win.selectedItem) await click(from, 0)
    }
    for (let i = 0; i < 40 && !win.slots[0]; i++) await sleep(50)
    if (!win.slots[0]) throw new Error('no crafting result appeared')
    await click(0, 0)
    await click(win.firstEmptyInventorySlot(), 0)
  } finally {
    if (recipe.requiresTable) bot.closeWindow(win)
    await sleep(250)
  }
}

async function craft(name) {
  const ids = Object.values(mcData.itemsByName).filter(i => itemMatch(name)(i.name)).map(i => i.id)
  const table = station('crafting_table')
  let recipe = null
  for (const id of ids) { recipe = bot.recipesFor(id, null, 1, table || null)[0]; if (recipe) break }
  if (!recipe) return { ok: false, msg: `cannot craft ${name}: missing ingredients${table ? '' : ' or no crafting table nearby'}` }
  if (recipe.requiresTable) await withTimeout(bot.pathfinder.goto(new goals.GoalNear(table.position.x, table.position.y, table.position.z, 2)), 60000, 'path to table')
  const before = count(name)
  try { await craftOnce(recipe, table) } catch (e) { console.log('craft err', e.message); return { ok: false, msg: `crafting ${name} failed: ${e.message}` } }
  return { ok: count(name) > before, msg: `crafted ${count(name) - before} ${name}` }
}

async function place(name) {
  const item = bot.inventory.items().find(i => i.name === name)
  if (!item) return { ok: false, msg: `no ${name} in the inventory` }
  const p = bot.entity.position.floored()
  for (let r = 1; r <= 3; r++) for (let dx = -r; dx <= r; dx++) for (let dz = -r; dz <= r; dz++) for (const dy of [0, 1, -1]) {
    if (Math.max(Math.abs(dx), Math.abs(dz)) !== r) continue
    const ref = bot.blockAt(p.offset(dx, dy - 1, dz)), above = bot.blockAt(p.offset(dx, dy, dz))
    if (!ref || !above || ref.boundingBox !== 'block' || above.name !== 'air') continue
    try {
      await bot.equip(item, 'hand')
      await bot.lookAt(ref.position.offset(0.5, 1, 0.5))
      await bot.placeBlock(ref, new Vec3(0, 1, 0))
      return { ok: true, msg: `placed ${name}` }
    } catch (e) { console.log('place err', e.message) }
  }
  return { ok: false, msg: `no free spot to place ${name}` }
}

async function smelt(input) {
  const fb = station('furnace')
  if (!fb) return { ok: false, msg: 'no furnace nearby' }
  const raw = bot.inventory.items().find(i => i.name === input), fuel = bot.inventory.items().find(i => ITEMS.planks(i.name) || i.name === 'coal')
  if (!raw) return { ok: false, msg: `no ${input} in the inventory` }
  if (!fuel) return { ok: false, msg: 'no fuel (planks) in the inventory' }
  await withTimeout(bot.pathfinder.goto(new goals.GoalNear(fb.position.x, fb.position.y, fb.position.z, 2)), 60000, 'path to furnace')
  const f = await bot.openFurnace(fb), n = raw.count
  const nfuel = Math.min(fuel.count, fuel.name === 'coal' ? Math.ceil(n / 8) : Math.ceil(n * 2 / 3))
  await f.putFuel(fuel.type, null, nfuel); await f.putInput(raw.type, null, n)
  for (let t = 0; t < n * 12 + 8; t++) { await sleep(1000); const o = f.outputItem(); if (o && o.count >= n) break; if (!f.inputItem() && f.fuel <= 0 && t > 3) break }
  const out = f.outputItem()
  if (out) await f.takeOutput()
  if (f.inputItem()) await f.takeInput()
  f.close()
  return out ? { ok: true, msg: `smelted ${out.count} ${out.name}` } : { ok: false, msg: 'smelting produced nothing (not enough fuel?)' }
}

let heading = Math.random() * 2 * Math.PI  // kept per episode: a fresh random direction every call is a random walk that goes nowhere
async function explore() {
  const a = heading + (Math.random() - 0.5) * 0.6, p = bot.entity.position.clone()
  try { await withTimeout(bot.pathfinder.goto(new goals.GoalXZ(p.x + 60 * Math.cos(a), p.z + 60 * Math.sin(a))), 60000, 'explore') } catch (e) { heading += 1.2 }
  return { ok: true, msg: `walked ${Math.round(bot.entity.position.distanceTo(p))} blocks` }
}

async function reset(x, z) {
  bot.chat('/clear'); await sleep(200)
  // start on dry land with trees in sight (otherwise half of the episodes begin in the ocean)
  for (let k = 0; k < 12; k++) {
    bot.chat(`/spreadplayers ${x + 300 * k} ${z} 0 40 false ${bot.username}`); await sleep(4000)
    const feet = bot.blockAt(bot.entity.position.floored())
    if (findNear('log').length > 3 && feet && feet.name !== 'water') break
  }
  bad.clear(); heading = Math.random() * 2 * Math.PI
  return { ok: true, msg: 'reset to ' + bot.entity.position.floored().toString() }
}

let busy = false
http.createServer((req, res) => {
  let body = ''
  req.on('data', c => { body += c })
  req.on('end', async () => {
    const send = o => { res.writeHead(200, { 'content-type': 'application/json' }); res.end(JSON.stringify(o)) }
    if (!ready) return send({ ok: false, msg: 'bot not ready' })
    if (req.url === '/state') return send(state())
    if (busy) return send({ ok: false, msg: 'busy' })
    busy = true
    let out
    try {
      const a = JSON.parse(body || '{}')
      if (req.url === '/reset') out = await reset(a.x || 0, a.z || 0)
      else out = await withTimeout({ collect: () => collect(a.arg, a.n || 1), craft: () => craft(a.arg), place: () => place(a.arg), smelt: () => smelt(a.arg), explore }[a.skill](), 240000, a.skill)
    } catch (e) { out = { ok: false, msg: 'error: ' + e.message } }
    busy = false
    send({ ...out, state: state() })
  })
}).listen(+opt('--http', 3007), '127.0.0.1', () => console.log('skill server on', opt('--http', 3007)))
