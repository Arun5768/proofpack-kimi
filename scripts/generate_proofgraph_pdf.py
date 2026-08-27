from pathlib import Path
from textwrap import wrap

from reportlab.lib.colors import HexColor, white
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output" / "pdf" / "ProofGraph_Product_and_System_Design.pdf"

PAGE_W, PAGE_H = landscape(A4)
CREAM = HexColor("#F4F2E8")
INK = HexColor("#11140F")
MUTED = HexColor("#62665D")
GREEN = HexColor("#76951E")
GREEN_DARK = HexColor("#334214")
PALE_GREEN = HexColor("#E7ECD5")
PALE_ORANGE = HexColor("#F5E7D0")
LINE = HexColor("#D8D9CF")
CARD = HexColor("#FCFCF8")


def fit_lines(text, font, size, width):
    words = text.split()
    lines, current = [], ""
    for word in words:
        trial = word if not current else current + " " + word
        if stringWidth(trial, font, size) <= width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def paragraph(c, text, x, y, width, size=10, leading=14, color=INK, font="Helvetica", max_lines=None):
    lines = fit_lines(text, font, size, width)
    if max_lines:
        lines = lines[:max_lines]
    c.setFont(font, size)
    c.setFillColor(color)
    for line in lines:
        c.drawString(x, y, line)
        y -= leading
    return y


def footer(c, page, label="PROOFGRAPH / PRODUCT AND SYSTEM DESIGN"):
    c.setStrokeColor(LINE)
    c.line(32, 25, PAGE_W - 32, 25)
    c.setFillColor(MUTED)
    c.setFont("Helvetica", 6.8)
    c.drawString(32, 13, label)
    c.drawRightString(PAGE_W - 32, 13, f"{page:02d}")


def header(c, kicker, title, page):
    c.setFillColor(CREAM)
    c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    c.setFillColor(GREEN_DARK)
    c.setFont("Helvetica-Bold", 7.5)
    c.drawString(32, PAGE_H - 37, kicker.upper())
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 24)
    c.drawString(32, PAGE_H - 69, title)
    footer(c, page)


def card(c, x, y, w, h, title, body, accent=GREEN, number=None):
    c.setFillColor(CARD)
    c.setStrokeColor(LINE)
    c.roundRect(x, y, w, h, 10, fill=1, stroke=1)
    c.setFillColor(accent)
    c.rect(x, y + h - 5, w, 5, fill=1, stroke=0)
    if number is not None:
        c.setFillColor(accent)
        c.circle(x + 20, y + h - 28, 11, fill=1, stroke=0)
        c.setFillColor(white)
        c.setFont("Helvetica-Bold", 8)
        c.drawCentredString(x + 20, y + h - 31, str(number))
        tx = x + 38
    else:
        tx = x + 16
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 10.5)
    c.drawString(tx, y + h - 31, title)
    paragraph(c, body, x + 16, y + h - 51, w - 32, size=8.2, leading=11, color=MUTED, max_lines=6)


def arrow(c, x1, y1, x2, y2, color=GREEN):
    c.setStrokeColor(color)
    c.setFillColor(color)
    c.setLineWidth(1.5)
    c.line(x1, y1, x2, y2)
    if x2 >= x1:
        points = [(x2, y2), (x2 - 7, y2 + 4), (x2 - 7, y2 - 4)]
    else:
        points = [(x2, y2), (x2 + 7, y2 + 4), (x2 + 7, y2 - 4)]
    path = c.beginPath()
    path.moveTo(*points[0])
    path.lineTo(*points[1])
    path.lineTo(*points[2])
    path.close()
    c.drawPath(path, fill=1, stroke=0)


def pill(c, text, x, y, color=PALE_GREEN, text_color=GREEN_DARK):
    w = stringWidth(text.upper(), "Helvetica-Bold", 6.8) + 18
    c.setFillColor(color)
    c.roundRect(x, y, w, 18, 9, fill=1, stroke=0)
    c.setFillColor(text_color)
    c.setFont("Helvetica-Bold", 6.8)
    c.drawCentredString(x + w / 2, y + 6, text.upper())
    return x + w + 7


def page_cover(c):
    c.setFillColor(CREAM)
    c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    c.setFillColor(INK)
    c.roundRect(30, PAGE_H - 67, 31, 31, 8, fill=1, stroke=0)
    c.setFillColor(GREEN)
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(45.5, PAGE_H - 57, "P")
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(69, PAGE_H - 56, "ProofGraph")

    c.setFillColor(GREEN_DARK)
    c.setFont("Helvetica-Bold", 8)
    c.drawString(32, PAGE_H - 128, "PRODUCT AND SYSTEM DESIGN / VERSION 0.1")

    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 39)
    c.drawString(32, PAGE_H - 185, "Evidence before")
    c.setFillColor(GREEN)
    c.drawString(32, PAGE_H - 229, "confidence.")

    paragraph(
        c,
        "A practical design for turning scattered work into evidence-backed decisions, reports, applications, and public records with Kimi.",
        34,
        PAGE_H - 271,
        410,
        size=13,
        leading=18,
        color=MUTED,
    )

    x = 34
    for item in ["Kimi K2.5", "Evidence graph", "Human resolution", "Code validation"]:
        x = pill(c, item, x, PAGE_H - 331)

    c.setFillColor(INK)
    c.roundRect(515, 82, 290, 402, 20, fill=1, stroke=0)
    c.setFillColor(PALE_GREEN)
    c.roundRect(544, 388, 232, 61, 12, fill=1, stroke=0)
    c.setFillColor(GREEN_DARK)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(562, 424, "01 / MAP THE EVIDENCE")
    c.setFont("Helvetica", 8)
    c.drawString(562, 406, "facts / conflicts / unknowns / risks")
    arrow(c, 660, 382, 660, 353, color=GREEN)
    c.setFillColor(white)
    c.roundRect(544, 285, 232, 61, 12, fill=1, stroke=0)
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(562, 321, "02 / BUILD INSIDE THE BOUNDARY")
    c.setFont("Helvetica", 8)
    c.drawString(562, 303, "cited deliverable / warnings / recipe")
    arrow(c, 660, 279, 660, 250, color=GREEN)
    c.setFillColor(PALE_ORANGE)
    c.roundRect(544, 182, 232, 61, 12, fill=1, stroke=0)
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(562, 218, "03 / VALIDATE WITHOUT ANOTHER MODEL")
    c.setFont("Helvetica", 8)
    c.drawString(562, 200, "source IDs / structure / ownership / bounds")
    footer(c, 1)


def page_problem(c):
    header(c, "01 / Product position", "A common problem hiding in different workflows", 2)
    paragraph(
        c,
        "People rarely lack work. They lack one reliable place that explains what happened, which record is final, and what can be claimed without exaggeration.",
        32,
        PAGE_H - 101,
        760,
        size=12,
        leading=17,
        color=MUTED,
    )
    specs = [
        ("Student builder", "Repositories, demos, certificates, event work and notes are disconnected.", "Verifiable portfolio case study"),
        ("NGO / community", "Registration, check-ins, photos, surveys and reports often disagree.", "Partner or donor impact report"),
        ("Founder", "Customer calls, experiments, market research and decisions lose their context.", "Evidence-backed decision memo"),
        ("Creator / researcher", "Large source sets make weak claims easy to repeat and hard to trace.", "Cited brief or article outline"),
    ]
    start_x, y, w, h, gap = 32, 298, 184, 145, 12
    for i, (name, problem, output) in enumerate(specs):
        x = start_x + i * (w + gap)
        card(c, x, y, w, h, name, problem, number=i + 1)
        c.setFillColor(PALE_GREEN)
        c.roundRect(x + 13, y + 14, w - 26, 32, 8, fill=1, stroke=0)
        paragraph(c, output, x + 22, y + 33, w - 44, size=7.3, leading=9, color=GREEN_DARK, font="Helvetica-Bold", max_lines=2)

    c.setFillColor(INK)
    c.roundRect(32, 80, PAGE_W - 64, 180, 14, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 13)
    c.drawString(54, 226, "The product promise")
    promises = [
        "Show what the supplied evidence supports.",
        "Expose conflicts, uncertainty and missing proof.",
        "Ask a human before resolving material disagreement.",
        "Create useful outputs with traceable source IDs.",
        "Validate mechanical guarantees in ordinary code.",
    ]
    for i, item in enumerate(promises):
        yb = 194 - i * 24
        c.setFillColor(GREEN)
        c.circle(60, yb + 2, 4, fill=1, stroke=0)
        c.setFillColor(white)
        c.setFont("Helvetica", 9)
        c.drawString(74, yb - 2, item)


def page_flow(c):
    header(c, "02 / Core workflow", "From raw material to a defensible output", 3)
    paragraph(
        c,
        "The model does two different jobs. A human resolves material conflicts. Code checks the guarantees that do not require model judgment.",
        32,
        PAGE_H - 102,
        760,
        size=11,
        leading=16,
        color=MUTED,
    )

    nodes = [
        ("1", "Capture", "Files, repos, pages, sheets, screenshots, notes"),
        ("2", "Normalize", "Stable source IDs and provenance metadata"),
        ("3", "Kimi maps", "Facts, conflicts, unknowns, injected instructions"),
        ("4", "Human gate", "Resolve high-impact disagreements explicitly"),
        ("5", "Kimi builds", "Cited deliverable inside the approved boundary"),
        ("6", "Code validates", "Source IDs, structure, confidence and ownership"),
    ]
    w, h, gap, start_x, y = 116, 112, 14, 32, 323
    for i, (num, title, body) in enumerate(nodes):
        x = start_x + i * (w + gap)
        card(c, x, y, w, h, title, body, number=num)
        if i < len(nodes) - 1:
            arrow(c, x + w + 2, y + h / 2, x + w + gap - 2, y + h / 2)

    c.setFillColor(PALE_GREEN)
    c.roundRect(32, 176, 378, 112, 14, fill=1, stroke=0)
    c.setFillColor(GREEN_DARK)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(52, 257, "What the human sees")
    paragraph(c, "97 appears in the organizer record. 143 appears in a draft caption. Which figure should be approved for the final report?", 52, 232, 330, size=9.2, leading=14, color=GREEN_DARK)

    c.setFillColor(PALE_ORANGE)
    c.roundRect(432, 176, 378, 112, 14, fill=1, stroke=0)
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(452, 257, "What code can guarantee")
    paragraph(c, "Every cited source ID exists. Required fields are present. Confidence is bounded. The saved result belongs to the authenticated account.", 452, 232, 330, size=9.2, leading=14, color=INK)

    c.setFillColor(INK)
    c.roundRect(32, 66, PAGE_W - 64, 75, 12, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, 112, "Boundary: ProofGraph does not claim to prove universal truth.")
    c.setFont("Helvetica", 9)
    c.setFillColor(HexColor("#D7D9D0"))
    c.drawString(50, 89, "It makes the supplied evidence, conflicts, decisions and validation steps visible enough to audit.")


def page_architecture(c):
    header(c, "03 / Internal design", "A small architecture with explicit responsibility", 4)
    paragraph(c, "Each layer owns a different kind of trust. The model is powerful, but it is not responsible for authentication, cost control or referential integrity.", 32, PAGE_H - 102, 760, size=11, leading=16, color=MUTED)

    columns = [
        ("Experience", ["Responsive client", "Evidence capture", "Conflict review", "Export and sharing"], PALE_GREEN),
        ("Application", ["Cloudflare Worker API", "Authentication", "Ownership checks", "Input and daily limits"], PALE_ORANGE),
        ("Reasoning", ["Kimi Context Mapper", "Kimi Deliverable Builder", "Structured contracts", "Prompt-injection flags"], PALE_GREEN),
        ("Records", ["Evidence graph", "Run history", "Decision trail", "Deterministic validation"], PALE_ORANGE),
    ]
    x0, y0, w, h, gap = 32, 190, 184, 286, 12
    for i, (name, items, bg) in enumerate(columns):
        x = x0 + i * (w + gap)
        c.setFillColor(bg)
        c.roundRect(x, y0, w, h, 15, fill=1, stroke=0)
        c.setFillColor(INK)
        c.setFont("Helvetica-Bold", 14)
        c.drawString(x + 18, y0 + h - 34, name)
        for j, item in enumerate(items):
            yy = y0 + h - 76 - j * 47
            c.setFillColor(CARD)
            c.roundRect(x + 14, yy - 20, w - 28, 34, 7, fill=1, stroke=0)
            c.setFillColor(INK)
            c.setFont("Helvetica", 8.6)
            c.drawString(x + 27, yy - 8, item)

    c.setFillColor(INK)
    c.roundRect(32, 64, PAGE_W - 64, 92, 12, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 10.5)
    c.drawString(50, 125, "Current production boundaries")
    boundary = "Server-side provider secret  |  authenticated runs  |  account ownership  |  source and block caps  |  per-user and global quotas  |  same-origin writes"
    paragraph(c, boundary, 50, 101, PAGE_W - 100, size=8.8, leading=13, color=HexColor("#D7D9D0"))


def page_roadmap(c):
    header(c, "04 / Delivery and measurement", "Start narrow, learn from corrections, then scale", 5)
    paragraph(c, "The current build proves the workflow. The roadmap adds provenance, human resolution and accessible capture before expanding into organization-scale infrastructure.", 32, PAGE_H - 102, 760, size=11, leading=16, color=MUTED)

    phases = [
        ("NOW", "Working proof", ["ProofPack workspace", "Two Kimi stages", "Code validator", "Auth, D1, quotas, export"]),
        ("NEXT", "Evidence graph", ["Source provenance", "Human conflict gate", "Reusable evidence packs", "Regression fixtures"]),
        ("THEN", "Accessible capture", ["Hindi-English workflows", "Mobile scans and voice", "Role-specific templates", "Reviewer access"]),
        ("SCALE", "Community infrastructure", ["Proof-of-work clinics", "Organization approvals", "Public impact records", "Workflow library"]),
    ]
    x0, y0, w, h, gap = 32, 271, 184, 195, 12
    for i, (tag, title, items) in enumerate(phases):
        x = x0 + i * (w + gap)
        c.setFillColor(CARD)
        c.setStrokeColor(LINE)
        c.roundRect(x, y0, w, h, 14, fill=1, stroke=1)
        c.setFillColor(GREEN if i == 0 else INK)
        c.roundRect(x + 15, y0 + h - 36, 43, 20, 10, fill=1, stroke=0)
        c.setFillColor(white)
        c.setFont("Helvetica-Bold", 6.6)
        c.drawCentredString(x + 36.5, y0 + h - 29, tag)
        c.setFillColor(INK)
        c.setFont("Helvetica-Bold", 11)
        c.drawString(x + 15, y0 + h - 63, title)
        for j, item in enumerate(items):
            yy = y0 + h - 92 - j * 24
            c.setFillColor(GREEN)
            c.circle(x + 20, yy + 2, 3, fill=1, stroke=0)
            c.setFillColor(MUTED)
            c.setFont("Helvetica", 8)
            c.drawString(x + 31, yy - 1, item)

    c.setFillColor(PALE_GREEN)
    c.roundRect(32, 151, 502, 84, 13, fill=1, stroke=0)
    c.setFillColor(GREEN_DARK)
    c.setFont("Helvetica-Bold", 10.5)
    c.drawString(50, 207, "Measure product quality")
    paragraph(c, "Conflicts surfaced / unsupported claims blocked / human corrections reused / time to approved output", 50, 182, 455, size=8.8, leading=13, color=GREEN_DARK)

    c.setFillColor(PALE_ORANGE)
    c.roundRect(552, 151, 258, 84, 13, fill=1, stroke=0)
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 10.5)
    c.drawString(570, 207, "Measure adoption")
    paragraph(c, "First evidence pack / repeat workflows / exported outputs / multilingual completion", 570, 182, 220, size=8.8, leading=13, color=INK)

    c.setFillColor(INK)
    c.roundRect(32, 62, PAGE_W - 64, 61, 12, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(PAGE_W / 2, 91, "A convincing response is an output. An inspectable process is a product.")


def page_proof(c):
    header(c, "05 / Existing proof", "Version zero is already running in public", 6)
    paragraph(c, "ProofPack and Kimi Workflow Lab demonstrate the technical core today. The results below describe one bounded synthetic test, not a general reliability claim.", 32, PAGE_H - 102, 760, size=11, leading=16, color=MUTED)

    stats = [
        ("5", "source blocks"),
        ("2", "Kimi model stages"),
        ("5/5", "code checks passed"),
        ("27.055 s", "recorded live latency"),
    ]
    for i, (value, label) in enumerate(stats):
        x = 32 + i * 196
        c.setFillColor(CARD)
        c.setStrokeColor(LINE)
        c.roundRect(x, 366, 184, 102, 13, fill=1, stroke=1)
        c.setFillColor(GREEN if i < 3 else INK)
        c.setFont("Helvetica-Bold", 23)
        c.drawString(x + 17, 419, value)
        c.setFillColor(MUTED)
        c.setFont("Helvetica", 8)
        c.drawString(x + 17, 393, label)

    c.setFillColor(INK)
    c.roundRect(32, 184, 500, 145, 14, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(52, 296, "Observed in the disposable run")
    observations = [
        "Selected the organizer record of 97 over an unverified draft of 143.",
        "Flagged the instruction to invent 10,000 attendees and an award.",
        "Preserved measurable follow-up: eight repositories and three session requests.",
        "Used only source IDs that existed in the submitted evidence pack.",
    ]
    for i, item in enumerate(observations):
        y = 268 - i * 26
        c.setFillColor(GREEN)
        c.circle(57, y + 2, 3.5, fill=1, stroke=0)
        c.setFillColor(HexColor("#ECEDE7"))
        c.setFont("Helvetica", 8.3)
        c.drawString(69, y - 1, item)

    c.setFillColor(PALE_ORANGE)
    c.roundRect(552, 184, 258, 145, 14, fill=1, stroke=0)
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(571, 296, "What this does not prove")
    paragraph(c, "The sources were synthetic. The validator checks references and structure, not external factual truth. A permission-safe evaluation set is the next requirement.", 571, 266, 219, size=9, leading=14, color=INK)

    c.setFillColor(PALE_GREEN)
    c.roundRect(32, 62, PAGE_W - 64, 86, 12, fill=1, stroke=0)
    c.setFillColor(GREEN_DARK)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(50, 119, "Inspect the working system")
    links = "Live lab: proofpack-kimi-arun.arunchandel1780.workers.dev/lab    |    Source: github.com/Arun5768/proofpack-kimi"
    paragraph(c, links, 50, 94, PAGE_W - 100, size=8.8, leading=13, color=GREEN_DARK)


def build_pdf():
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(OUTPUT), pagesize=(PAGE_W, PAGE_H), pageCompression=1)
    c.setTitle("ProofGraph - Product and System Design")
    c.setAuthor("Arun Pratap Singh Chandel")
    c.setSubject("Evidence-first product architecture built from ProofPack and Kimi Workflow Lab")

    for page in [page_cover, page_problem, page_flow, page_architecture, page_roadmap, page_proof]:
        page(c)
        c.showPage()
    c.save()
    print(OUTPUT)


if __name__ == "__main__":
    build_pdf()

