"""ÉLVARÉ product catalog — single source of truth.

All products, names and descriptions are fictional and created for a demonstration store.
build_site.py writes this to assets/js/products.js; build_images.py renders imagery from it.
"""

C = {  # colour library: name -> hex
    "Obsidian": "#1a1a1a", "Ivory": "#efe8db", "Camel": "#b38b5d", "Stone": "#cfc6b6",
    "Charcoal": "#3a3a3a", "Champagne": "#d9c39a", "Bordeaux": "#5e1f2a", "Navy": "#1f2a3d",
    "Sage": "#8f9a83", "Cognac": "#8a4f2a", "Ecru": "#e6dcc8", "Graphite": "#4a4c50",
    "Sand": "#d5c2a1", "Chocolate": "#4a3227", "Pearl": "#ece9e4", "Olive": "#5d5e43",
    "Sky": "#b9c6d2", "Rosewater": "#d9b8ae", "Tobacco": "#6b4a2e", "White": "#f7f6f2",
    "Garnet": "#7a1f2b", "Forest": "#2f4a3a", "Cobalt": "#2a4fa8", "Violet": "#6a4c9c", "Plum": "#4e2a4f",
    "Taupe": "#8b7d6b", "Khaki": "#a8946b", "Teal": "#1f5f63", "Blush": "#e3c4bf", "Oxblood": "#4a1c1c",
}

W_SIZES = ["XS", "S", "M", "L", "XL"]
M_SIZES = ["S", "M", "L", "XL", "XXL"]
W_TROUSER = ["24", "26", "28", "30", "32"]
M_TROUSER = ["28", "30", "32", "34", "36"]
W_SHOE = ["36", "37", "38", "39", "40", "41"]
M_SHOE = ["40", "41", "42", "43", "44", "45"]
ONE = ["One Size"]
M_BELT = ["80", "85", "90", "95", "100"]

# fields: id, name, gender, category, shape(for renderer), price, colours, sizes, collections, tags,
#         availability, popularity, added(ISO), description, details
P = [
    # ---------------- WOMEN ----------------
    ("EW-101", "Céleste Silk Slip Dress", "women", "dresses", "slipdress", 385, ["Champagne", "Obsidian", "Garnet"], W_SIZES,
     ["signature", "evening"], ["silk", "evening", "bias-cut"], "in_stock", 96, "2026-10-28",
     "A bias-cut slip dress in fluid silk satin that skims the body and pools gently at the ankle. Fine adjustable straps and a softly draped cowl neckline make it equally at home under tailoring or worn alone for evening.",
     ["100% silk satin", "Bias cut with cowl neckline", "Adjustable straps", "Midi-to-maxi length", "Dry clean only"]),
    ("EW-102", "Isaure Column Dress", "women", "dresses", "columndress", 420, ["Obsidian", "Ivory"], W_SIZES,
     ["evening", "signature"], ["crepe", "evening", "long-sleeve"], "low_stock", 88, "2026-09-14",
     "A floor-length column in heavyweight crepe with a high neck and long, narrow sleeves. The architecture is in the restraint: a single concealed back zip and a clean, unbroken line from shoulder to hem.",
     ["Heavyweight crepe", "High neckline, long sleeves", "Concealed back zip", "Floor length", "Dry clean only"]),
    ("EW-103", "Aurelle Wrap Midi Dress", "women", "dresses", "wrapdress", 295, ["Forest", "Cobalt", "Violet"], W_SIZES,
     ["resort", "essentials"], ["wrap", "day-to-evening"], "in_stock", 74, "2026-08-02",
     "A wrap-front midi dress in a fluid fabric with weight and movement. The self-tie waist adjusts to the wearer, and the midi hem moves beautifully from office to dinner.",
     ["Fluid viscose-blend fabric", "Wrap front with self-tie waist", "Sleeve length varies by colourway", "Midi length", "Machine wash cold, delicate"]),
    ("EW-104", "Solenne Poplin Shirt", "women", "tops", "shirt", 165, ["White", "Sky"], W_SIZES,
     ["essentials", "tailored"], ["cotton", "poplin", "oversized"], "in_stock", 91, "2026-10-05",
     "Our signature shirt in crisp cotton poplin with a relaxed, slightly dropped shoulder. A concealed placket and elongated cuffs keep the silhouette clean and quietly considered.",
     ["Crisp cotton poplin", "Relaxed fit, dropped shoulder", "Concealed button placket", "Elongated cuffs", "Machine wash 30°C"]),
    ("EW-105", "Inès Silk Blouse", "women", "tops", "blouse", 178, ["Ivory", "Champagne", "Plum"], W_SIZES,
     ["evening", "signature"], ["silk", "blouse"], "in_stock", 69, "2026-09-22",
     "A fluid silk-satin shirt with a soft point collar and generous buttoned cuffs. Designed to tuck cleanly into tailored trousers or to be worn loose over a slip skirt.",
     ["Silk satin", "Soft point collar", "Buttoned cuffs", "Relaxed fit", "Dry clean only"]),
    ("EW-106", "Valère Double-Faced Wool Coat", "women", "jackets-coats", "longcoat", 780, ["Camel", "Charcoal", "Stone"], W_SIZES,
     ["signature", "tailored", "seasonal"], ["wool", "outerwear", "double-faced"], "in_stock", 99, "2026-10-30",
     "Constructed from double-faced wool with hand-finished seams, this long, enveloping coat has nothing to hide. A notch lapel and softly dropped shoulder create an effortlessly assured line.",
     ["Double-faced wool blend", "Hand-finished seams", "Notch lapel", "Below-knee length", "Specialist dry clean"]),
    ("EW-107", "Riviera Tailored Jacket", "women", "jackets-coats", "blazer", 540, ["Obsidian", "Ivory"], W_SIZES,
     ["tailored", "resort"], ["tailoring", "blazer"], "low_stock", 77, "2026-07-18",
     "A sharply cut single-breasted jacket with strong shoulders and sharply cut lapels. Pair with the Lise trouser for a modern suit or wear it over a slip dress for evening.",
     ["Wool-blend suiting", "Structured shoulder", "Single-breasted front", "Fully lined", "Dry clean only"]),
    ("EW-108", "Alba Wide-Leg Trouser", "women", "trousers", "widetrouser", 245, ["Sand", "Olive", "Bordeaux"], W_TROUSER,
     ["tailored", "essentials"], ["tailoring", "wide-leg", "high-rise"], "in_stock", 93, "2026-09-03",
     "A high-rise trouser with a generous wide leg that breaks softly over the shoe. Cut from a fluid fabric with natural drape and an easy, comfortable waist.",
     ["Fluid crepe-weave fabric", "High rise", "Side slip pockets", "Full-length wide leg", "Machine wash cold"]),
    ("EW-109", "Lise Cigarette Trouser", "women", "trousers", "slimtrouser", 195, ["Obsidian"], W_TROUSER,
     ["essentials", "tailored"], ["slim", "ankle-length"], "in_stock", 71, "2026-06-20",
     "A slim, ankle-grazing trouser with a pressed crease and a small side split at the hem. The quiet backbone of a working wardrobe.",
     ["Stretch cotton-blend twill", "Mid rise, slim leg", "Pressed front crease", "Ankle length with side split", "Machine wash 30°C"]),
    ("EW-110", "Noor Cashmere-Blend Crewneck", "women", "knitwear", "sweater", 320, ["Ecru", "Navy"], W_SIZES,
     ["essentials", "seasonal"], ["cashmere-blend", "knit", "crewneck"], "in_stock", 95, "2026-10-12",
     "A softly relaxed crewneck in a cashmere and wool blend, knitted for a light, airy handle. Ribbed trims and a slightly cropped body make it simple to layer.",
     ["Cashmere and wool blend", "Relaxed fit, slightly cropped", "Fine rib trims", "Mid-weight knit", "Hand wash cold"]),
    ("EW-111", "Odile Ribbed Cardigan", "women", "knitwear", "cardigan", 265, ["Ivory", "Sage"], W_SIZES,
     ["essentials", "resort"], ["knit", "cardigan", "ribbed"], "in_stock", 66, "2026-08-25",
     "A softly relaxed knitted cardigan with a deep V and tonal buttons. Wear it buttoned as a top or open over silk.",
     ["Wool-blend knit", "Relaxed silhouette", "Deep V neckline", "Tonal buttons", "Hand wash cold"]),
    ("EW-112", "Sabine Satin Midi Skirt", "women", "skirts", "slipskirt", 230, ["Obsidian"], W_SIZES,
     ["evening", "signature"], ["satin", "bias-cut", "midi"], "in_stock", 84, "2026-10-01",
     "A bias-cut satin skirt with a narrow elasticated waist and a fluid midi hem. Its quiet sheen catches the light with every step.",
     ["Heavy satin", "Bias cut", "Concealed elastic waist", "Midi length", "Dry clean only"]),
    ("EW-113", "Margaux Pleated Midi Skirt", "women", "skirts", "pleatskirt", 260, ["Obsidian", "Ivory"], W_SIZES,
     ["tailored", "seasonal"], ["pleated", "midi"], "in_stock", 58, "2026-09-09",
     "Fine pleats fall from a flat waistband in this fluid, below-the-knee skirt. Structured yet airy, it moves with deliberate grace.",
     ["Lightweight pleated fabric", "Fine knife pleats", "Flat waistband", "Below-knee to ankle length", "Hand wash cold"]),
    ("EW-114", "Étoile Top-Handle Bag", "women", "accessories", "bag", 250, ["Obsidian", "Teal"], ONE,
     ["signature", "evening"], ["leather", "bag"], "low_stock", 97, "2026-10-20",
     "A compact, structured top-handle bag in grained leather with a front flap and a polished gold-tone clasp. Sized for the essentials, with a detachable shoulder strap.",
     ["Grained leather", "Gold-tone flap clasp", "Detachable shoulder strap", "Interior slip pocket", "W 24 × H 18 × D 9 cm"]),
    ("EW-115", "Lumen Silk Square Scarf", "women", "accessories", "scarf", 135, ["Garnet", "Blush"], ONE,
     ["resort", "signature"], ["silk", "scarf"], "in_stock", 62, "2026-07-30",
     "A silk square with a hand-rolled edge, in a rich botanical print or a soft solid. Tie at the neck, through a bag handle, or in the hair.",
     ["Silk twill", "Hand-rolled edges", "Printed or solid colourways", "90 × 90 cm", "Dry clean only"]),
    ("EW-116", "Arc Pointed Leather Mule", "women", "accessories", "mule", 240, ["Ivory"], W_SHOE,
     ["evening", "signature"], ["footwear", "leather", "mule"], "in_stock", 81, "2026-10-08",
     "A pointed backless mule on a slender kitten heel, finished with a pearl-trimmed strap. Soft upper, cushioned lined footbed and a heel height that remains wearable from day into night.",
     ["Soft leather upper", "Pearl-trimmed strap", "5 cm kitten heel", "Pointed toe", "Comes with dust bag"]),
    # ---------------- MEN ----------------
    ("EM-201", "Ferrand Oxford Shirt", "men", "shirts", "mshirt", 150, ["White", "Sky", "Ecru"], M_SIZES,
     ["essentials", "tailored"], ["cotton", "oxford"], "in_stock", 90, "2026-09-18",
     "A clean, modern Oxford shirt with a soft roll collar and a slightly tapered body. Woven from a substantial cotton that softens with every wear.",
     ["Cotton Oxford cloth", "Soft roll collar", "Tapered regular fit", "Mother-of-pearl-effect buttons", "Machine wash 30°C"]),
    ("EM-202", "Delmar Linen Band-Collar Shirt", "men", "shirts", "campshirt", 165, ["White", "Sky", "Navy"], M_SIZES,
     ["resort", "seasonal"], ["linen", "band-collar", "short-sleeve"], "in_stock", 73, "2026-06-28",
     "A relaxed short-sleeve shirt in washed linen with a clean band collar and a straight hem designed to be worn untucked.",
     ["Washed linen", "Band collar", "Relaxed fit", "Straight hem", "Machine wash 30°C"]),
    ("EM-203", "Essential Pima Tee", "men", "t-shirts", "tee", 65, ["White", "Obsidian"], M_SIZES,
     ["essentials"], ["cotton", "t-shirt", "crewneck"], "in_stock", 98, "2026-08-10",
     "The foundation of the wardrobe: a mid-weight crewneck tee with a refined, slightly structured hand and a collar that holds its shape.",
     ["Mid-weight cotton jersey", "Reinforced crew neckline", "Regular fit", "Straight hem", "Machine wash 30°C"]),
    ("EM-204", "Heavyweight Mock-Neck Tee", "men", "t-shirts", "mocktee", 92, ["Ecru"], M_SIZES,
     ["essentials", "seasonal"], ["cotton", "mock-neck"], "in_stock", 79, "2026-10-14",
     "A dense, heavyweight ribbed-knit tee with a low mock neck and a clean cut that layers effortlessly beneath tailoring.",
     ["Heavyweight cotton rib knit", "Low mock neck", "Regular fit", "Short sleeves", "Machine wash 30°C"]),
    ("EM-205", "Rivoli Pleated Wool Trouser", "men", "trousers", "mtrouser", 265, ["Taupe", "Olive", "Chocolate"], M_TROUSER,
     ["tailored", "signature"], ["wool", "pleated", "tailoring"], "in_stock", 86, "2026-09-26",
     "A pleated wool trouser with a gently tapered leg and a clean waistband — a refined nod to classic tailoring, cut to pair with its matching jacket.",
     ["Tropical-weight wool", "Front pleats", "Belt loops", "Tapered leg", "Dry clean only"]),
    ("EM-206", "Corso Tapered Chino", "men", "trousers", "mchino", 160, ["Sand", "Khaki"], M_TROUSER,
     ["essentials", "resort"], ["cotton", "chino"], "in_stock", 82, "2026-07-12",
     "A clean-front chino in brushed cotton twill with a mid rise and a tapered leg. Smart enough for the office, relaxed enough for the weekend.",
     ["Brushed cotton twill", "Mid rise, flat front", "Tapered leg", "Concealed coin pocket", "Machine wash 30°C"]),
    ("EM-207", "Bastien Unstructured Blazer", "men", "jackets", "mblazer", 595, ["Navy", "Charcoal"], M_SIZES,
     ["tailored", "signature"], ["tailoring", "unstructured"], "in_stock", 89, "2026-10-03",
     "An unstructured two-button blazer with a natural shoulder and patch pockets. Half-lined for ease, it drapes like a cardigan and reads like tailoring.",
     ["Wool-blend hopsack", "Natural, unpadded shoulder", "Half-lined", "Patch pockets", "Dry clean only"]),
    ("EM-208", "Halden Suede Overshirt Jacket", "men", "jackets", "overshirt", 640, ["Tobacco", "Olive", "Taupe"], M_SIZES,
     ["signature", "seasonal"], ["suede", "overshirt"], "low_stock", 75, "2026-10-22",
     "A supple suede overshirt with a button front and twin chest pockets. Worn as a light jacket over knitwear or buttoned as a shirt.",
     ["Supple goat suede", "Button front", "Twin flap chest pockets", "Cotton lining", "Specialist leather clean"]),
    ("EM-209", "Aldric Merino Rollneck", "men", "knitwear", "rollneck", 230, ["Ecru", "Obsidian", "Bordeaux"], M_SIZES,
     ["essentials", "seasonal"], ["merino", "rollneck", "knit"], "in_stock", 87, "2026-10-17",
     "A fine-gauge merino rollneck with a close, clean fit. The definitive layer under a blazer or overcoat.",
     ["Fine-gauge merino wool", "Folded rollneck", "Slim fit", "Ribbed cuffs and hem", "Hand wash cold"]),
    ("EM-210", "Teodor Wool Cardigan", "men", "knitwear", "mcardigan", 340, ["Ecru", "Obsidian"], M_SIZES,
     ["seasonal", "signature"], ["knit", "cardigan", "wool"], "in_stock", 64, "2026-10-26",
     "A substantial wool-blend cardigan with a softly textured knit and tonal buttons. Generous, warm and built for colder seasons.",
     ["Wool-blend knit", "Button front", "Tonal buttons", "Ribbed cuffs and hem", "Hand wash cold"]),
    ("EM-211", "Varenne Wool Overcoat", "men", "outerwear", "overcoat", 890, ["Camel", "Stone", "Tobacco"], M_SIZES,
     ["signature", "tailored", "seasonal"], ["wool", "overcoat", "outerwear"], "in_stock", 94, "2026-10-29",
     "An overcoat in dense wool with a notch lapel and a clean, knee-length line. Fully lined and cut to sit comfortably over tailoring.",
     ["Dense wool blend", "Notch lapel", "Fully lined", "Knee length", "Specialist dry clean"]),
    ("EM-212", "Harbor Quilted Jacket", "men", "outerwear", "fieldcoat", 560, ["Navy", "Olive"], M_SIZES,
     ["seasonal", "essentials"], ["quilted", "outerwear"], "preorder", 61, "2026-11-02",
     "A lightweight quilted jacket with a stand collar and a clean zip front. Warm without bulk.",
     ["Quilted shell with light padding", "Stand collar", "Zip-front pockets", "Zip front", "Machine wash cold"]),
    ("EM-213", "Ledger Leather Belt", "men", "accessories", "belt", 120, ["Cognac", "Chocolate", "Navy"], M_BELT,
     ["essentials", "tailored"], ["leather", "belt"], "in_stock", 72, "2026-08-14",
     "A belt in full-grain leather with a brushed metal buckle — smooth in cognac, stitched and burnished in chocolate and navy.",
     ["Full-grain leather", "Brushed metal buckle", "3.5 cm width", "Finish varies by colourway", "Sizes in cm"]),
    ("EM-214", "Saline Leather Derby", "men", "accessories", "derby", 248, ["Chocolate", "Oxblood"], M_SHOE,
     ["tailored", "signature"], ["footwear", "leather", "derby"], "in_stock", 85, "2026-09-30",
     "A refined plain-toe Derby in polished leather on a slim, low-profile sole. Equally considered with a suit or a chino.",
     ["Polished leather upper", "Leather lining", "Slim low-profile sole", "Plain toe, open lacing", "Comes with dust bags"]),
    ("EM-215", "Cassis Wool-Cashmere Scarf", "men", "accessories", "mscarf", 175, ["Charcoal", "Stone"], ONE,
     ["seasonal", "essentials"], ["cashmere-blend", "scarf"], "in_stock", 68, "2026-10-19",
     "A generously sized scarf in a soft wool and cashmere blend — chunky in charcoal, finely woven with fringed ends in stone.",
     ["Wool and cashmere blend", "Knit or woven by colourway", "190 × 35 cm", "Brushed finish", "Dry clean only"]),
    ("EM-216", "Atelier Card Holder", "men", "accessories", "cardholder", 85, ["Cognac", "Obsidian"], ONE,
     ["essentials", "signature"], ["leather", "small-leather-goods"], "in_stock", 76, "2026-09-12",
     "A slim, hand-stitched leather card holder with a central pocket for notes and cards. Unbranded and quietly made to soften with use.",
     ["Full-grain leather", "Hand-stitched edges", "Central pocket", "Holds up to six cards", "W 10 × H 7.5 cm"]),
]

CATEGORIES = {
    "women": [("new", "New Arrivals"), ("dresses", "Dresses"), ("tops", "Tops & Shirts"), ("jackets-coats", "Jackets & Coats"),
              ("trousers", "Trousers"), ("knitwear", "Knitwear"), ("skirts", "Skirts"), ("accessories", "Accessories")],
    "men": [("new", "New Arrivals"), ("shirts", "Shirts"), ("t-shirts", "T-Shirts"), ("trousers", "Trousers"),
            ("jackets", "Jackets"), ("knitwear", "Knitwear"), ("outerwear", "Outerwear"), ("accessories", "Accessories")],
}

COLLECTIONS = [
    ("signature", "The Signature Collection", "The defining pieces of the house — cut with intent, made to be kept."),
    ("essentials", "Modern Essentials", "The quiet foundations of a considered wardrobe, refined season after season."),
    ("evening", "Evening Edit", "Silk, satin and shadow. Pieces composed for the hours after dusk."),
    ("tailored", "The Tailored Collection", "Precise shoulders, fluid lines and tailoring that moves with you."),
    ("resort", "Resort Collection", "Light fabrics and sunlit tones for warmer horizons."),
    ("seasonal", "Seasonal Arrivals", "Autumn–Winter 2026: wool, cashmere-blend and the colours of late light."),
]


def slugify(s):
    import unicodedata, re
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def products():
    out = []
    newest = sorted(P, key=lambda p: p[12], reverse=True)[:12]
    new_ids = {p[0] for p in newest}
    for (pid, name, g, cat, shape, price, cols, sizes, colls, tags, avail, pop, added, desc, details) in P:
        slug = slugify(name)
        out.append({
            "id": pid, "slug": slug, "name": name, "gender": g, "category": cat, "shape": shape,
            "price": price, "colors": [{"name": c, "hex": C[c], "key": slugify(c)} for c in cols],
            "sizes": sizes, "collections": colls, "tags": tags, "availability": avail,
            "popularity": pop, "added": added, "isNew": pid in new_ids,
            "bestseller": pop >= 90, "description": desc, "details": details,
            "image": f"assets/img/products/{slug}-{slugify(cols[0])}",
        })
    return out


if __name__ == "__main__":
    ps = products()
    print(len(ps), "products;", sum(p["gender"] == "women" for p in ps), "women /", sum(p["gender"] == "men" for p in ps), "men")
    print("new:", [p["id"] for p in ps if p["isNew"]])
    print("best:", [p["id"] for p in ps if p["bestseller"]])
