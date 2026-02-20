with open('index.html', 'r', encoding='utf-8') as f:
    c = f.read()

# Detect line ending
LF = '\r\n' if '\r\n' in c else '\n'
def L(*parts): return LF.join(parts)

# ── 1. State variables ─────────────────────────────────────────────────────────
old1 = "        let wSurfVal = 0;" + LF
new1 = ("        let wSurfVal = 0;" + LF +
        "        let surfMode = 'segment', surfGrad = 'viridis', surfSlices = 10, surfAlpha = 0.13;" + LF)
assert old1 in c, 'FAIL 1'
c = c.replace(old1, new1, 1)
print('1 OK')

# ── 2. updateWsurfSlider ───────────────────────────────────────────────────────
old2 = (
    "            // All models now use W, so always show the slider when regression is on" + LF +
    "            wsurfRow.style.display = showReg ? 'block' : 'none';" + LF +
    "            if (showReg) {" + LF
)
new2 = (
    "            const on = showReg;" + LF +
    "            wsurfRow.style.display  = (on && surfMode === 'segment') ? 'block' : 'none';" + LF +
    "            spaceOpts.style.display = (on && surfMode === 'space')   ? 'block' : 'none';" + LF +
    "            if (on) {" + LF
)
assert old2 in c, 'FAIL 2'
c = c.replace(old2, new2, 1)
print('2 OK')

# ── 3. Surface drawing: replace entire if-block ───────────────────────────────
header = "            // \u2500\u2500 Regression surface \u2500\u2500" + LF
start_idx = c.index(header)
depth = 0
i = start_idx + len(header)
while i < len(c):
    if c[i] == '{': depth += 1
    elif c[i] == '}':
        depth -= 1
        if depth == 0:
            end_idx = i + 1
            break
    i += 1

new_draw = (
    "            // \u2500\u2500 Regression surface \u2500\u2500" + LF +
    "            if (showReg && regResult) {" + LF +
    "                const STEPS = 12;" + LF +
    "                const allQuads = [];" + LF +
    "" + LF +
    "                function buildSlice(wVal, fillColor, strokeColor) {" + LF +
    "                    const grid = [];" + LF +
    "                    for (let i = 0; i <= STEPS; i++) {" + LF +
    "                        grid[i] = [];" + LF +
    "                        for (let j = 0; j <= STEPS; j++) {" + LF +
    "                            const xv = xMn + (xMx - xMn) * (i / STEPS);" + LF +
    "                            const yv = yMn + (yMx - yMn) * (j / STEPS);" + LF +
    "                            const fakeRow = { [colX]: xv, [colY]: yv, [colZ]: 0, [colW]: wVal };" + LF +
    "                            const zv = regResult.predict(fakeRow);" + LF +
    "                            const nzv = isFinite(zv) ? nz(Math.max(zMn, Math.min(zMx, zv))) : null;" + LF +
    "                            grid[i][j] = nzv !== null ? proj([nx(xv), ny(yv), nzv]) : null;" + LF +
    "                        }" + LF +
    "                    }" + LF +
    "                    for (let i = 0; i < STEPS; i++) for (let j = 0; j < STEPS; j++) {" + LF +
    "                        const p00=grid[i][j], p10=grid[i+1][j], p11=grid[i+1][j+1], p01=grid[i][j+1];" + LF +
    "                        if (!p00||!p10||!p11||!p01) continue;" + LF +
    "                        allQuads.push({ z:(p00[2]+p10[2]+p11[2]+p01[2])/4, pts:[p00,p10,p11,p01], fill:fillColor, stroke:strokeColor });" + LF +
    "                    }" + LF +
    "                }" + LF +
    "" + LF +
    "                if (surfMode === 'segment') {" + LF +
    "                    buildSlice(wSurfVal, 'rgba(139,92,246,0.18)', 'rgba(139,92,246,0.4)');" + LF +
    "                } else {" + LF +
    "                    const N = surfSlices;" + LF +
    "                    for (let k = 0; k < N; k++) {" + LF +
    "                        const wVal = wAbsMin + (wAbsMax - wAbsMin) * (k / Math.max(N - 1, 1));" + LF +
    "                        const wt = (wVal - wAbsMin) / (wAbsMax - wAbsMin || 1);" + LF +
    "                        const [rc, gc, bc] = sampleCmap(wt, surfGrad);" + LF +
    "                        buildSlice(wVal," + LF +
    "                            `rgba(${rc},${gc},${bc},${surfAlpha})`," + LF +
    "                            `rgba(${rc},${gc},${bc},${Math.min(1, surfAlpha * 2.5)})`" + LF +
    "                        );" + LF +
    "                    }" + LF +
    "                }" + LF +
    "" + LF +
    "                allQuads.sort((a, b) => a.z - b.z);" + LF +
    "                allQuads.forEach(({ pts:[p00,p10,p11,p01], fill, stroke }) => {" + LF +
    "                    ctx.beginPath();" + LF +
    "                    ctx.moveTo(p00[0],p00[1]); ctx.lineTo(p10[0],p10[1]);" + LF +
    "                    ctx.lineTo(p11[0],p11[1]); ctx.lineTo(p01[0],p01[1]); ctx.closePath();" + LF +
    "                    ctx.fillStyle = fill; ctx.fill();" + LF +
    "                    ctx.strokeStyle = stroke; ctx.lineWidth = 0.5; ctx.stroke();" + LF +
    "                });" + LF +
    "            }"
)
c = c[:start_idx] + new_draw + c[end_idx:]
print('3 OK')

# ── 4. DOM refs ────────────────────────────────────────────────────────────────
old4 = (
    "        const selModel = $('sel-model');" + LF +
    "        const wsurfRow = $('wsurf-row');" + LF +
    "        const rngWsurf = $('rng-wsurf');" + LF +
    "        const lblWsurf = $('lbl-wsurf');" + LF
)
new4 = (
    "        const selModel    = $('sel-model');" + LF +
    "        const selSurfmode = $('sel-surfmode');" + LF +
    "        const selSurfgrad = $('sel-surfgrad');" + LF +
    "        const wsurfRow    = $('wsurf-row');" + LF +
    "        const spaceOpts   = $('space-opts');" + LF +
    "        const rngWsurf    = $('rng-wsurf');" + LF +
    "        const lblWsurf    = $('lbl-wsurf');" + LF +
    "        const rngSlices   = $('rng-slices');" + LF +
    "        const lblSlices   = $('lbl-slices');" + LF +
    "        const rngSalpha   = $('rng-salpha');" + LF +
    "        const lblSalpha   = $('lbl-salpha');" + LF
)
assert old4 in c, 'FAIL 4'
c = c.replace(old4, new4, 1)
print('4 OK')

# ── 5. Event listeners ─────────────────────────────────────────────────────────
old5 = "        selModel.addEventListener('change', () => { updateWsurfSlider(); updateReg(); draw(); });" + LF
new5 = (
    "        selModel.addEventListener('change', () => { updateWsurfSlider(); updateReg(); draw(); });" + LF +
    "        selSurfmode.addEventListener('change', () => { surfMode = selSurfmode.value; updateWsurfSlider(); draw(); });" + LF +
    "        selSurfgrad.addEventListener('change', () => { surfGrad = selSurfgrad.value; draw(); });" + LF +
    "        rngSlices.addEventListener('input', () => { surfSlices = parseInt(rngSlices.value); lblSlices.textContent = surfSlices; draw(); });" + LF +
    "        rngSalpha.addEventListener('input', () => { surfAlpha = parseFloat(rngSalpha.value); lblSalpha.textContent = surfAlpha.toFixed(2); draw(); });" + LF
)
assert old5 in c, 'FAIL 5'
c = c.replace(old5, new5, 1)
print('5 OK')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(c)
print('Done.')
