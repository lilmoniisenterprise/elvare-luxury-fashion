# product slug -> list of (colour, group, idx); first entry is the default colour
P = {
 "celeste-silk-slip-dress": [("Champagne","slip",1),("Obsidian","slip",7),("Garnet","slip",9)],
 "isaure-column-dress": [("Obsidian","column",7),("Ivory","r2white",13)],
 "aurelle-wrap-midi-dress": [("Forest","wrap",2),("Cobalt","wrap",5),("Violet","wrap",3)],
 "solenne-poplin-shirt": [("White","wshirt",2),("Sky","wshirt",6)],
 "ines-silk-blouse": [("Ivory","r2silk",12),("Champagne","r2silk",11),("Plum","r2silk",5)],
 "valere-double-faced-wool-coat": [("Camel","wcoat",4),("Charcoal","wcoat",7),("Stone","wcoat",9)],
 "riviera-cropped-tailored-jacket": [("Obsidian","wblazer",5),("Ivory","wblazer",8)],
 "alba-wide-leg-trouser": [("Sand","wtrouser",4),("Olive","wtrouser",0),("Bordeaux","wtrouser",3)],
 "lise-cigarette-trouser": [("Obsidian","wtrouser",6)],
 "noor-cashmere-blend-crewneck": [("Ecru","r2crew",1),("Navy","r2crew",14),("Grey","r2crew",7)],
 "odile-ribbed-cardigan": [("Ivory","wknit",4),("Sage","wknit",9),("Obsidian","wknit",13)],
 "sabine-satin-midi-skirt": [("Champagne","skirt",1),("Obsidian","r2skirt",0)],
 "margaux-pleated-wool-skirt": [("Obsidian","skirt",18),("Ivory","skirt",12)],
 "etoile-top-handle-bag": [("Obsidian","bag",9),("Teal","bag",1),("Navy","bag",6)],
 "lumen-silk-square-scarf": [("Garnet","scarf",4),("Blush","scarf",12)],
 "arc-pointed-leather-mule": [("Obsidian","r2mule",1),("Ivory","r2mule",6)],
 "ferrand-oxford-shirt": [("White","mshirt",14),("Sky","mshirt",1),("Ecru","mshirt",13)],
 "delmar-linen-camp-shirt": [("White","linen",0),("Sky","linen",1),("Navy","linen",3)],
 "essential-pima-tee": [("White","tee",7),("Obsidian","tee",11),("Grey","tee",2)],
 "heavyweight-mock-neck-tee": [("Ecru","r2mock",1),("Sage","r2mock",3)],
 "rivoli-pleated-wool-trouser": [("Taupe","mtrouser",10),("Olive","mtrouser",4),("Chocolate","mtrouser",6)],
 "corso-tapered-chino": [("Sand","chino",13),("Khaki","chino",11),("White","chino",9)],
 "bastien-unstructured-blazer": [("Navy","mblazer",9),("Charcoal","mblazer",7)],
 "halden-suede-overshirt-jacket": [("Tobacco","suede",10),("Olive","suede",6),("Taupe","suede",1)],
 "aldric-merino-rollneck": [("Ecru","roll",11),("Obsidian","roll",4),("Bordeaux","roll",2)],
 "teodor-cable-cardigan": [("Ecru","mcard",4),("Obsidian","mcard",5)],
 "varenne-camel-overcoat": [("Camel","mcoat",1),("Stone","mcoat",2),("Tobacco","mcoat",0)],
 "harbor-quilted-field-coat": [("Navy","quilt",1),("Olive","quilt",11),("Obsidian","quilt",2)],
 "ledger-leather-belt": [("Cognac","belt",3),("Chocolate","belt",0),("Navy","belt",10)],
 "saline-leather-derby": [("Chocolate","derby",12),("Oxblood","derby",3),("Obsidian","derby",0)],
 "cassis-wool-cashmere-scarf": [("Charcoal","scarf",21),("Bordeaux","scarf",19),("Stone","scarf",16)],
 "atelier-card-holder": [("Cognac","card",0),("Obsidian","card",11),("Tan","card",6)],
}
EXTRA_ALT = {"bastien-unstructured-blazer": ("mblazer",1)}
CAMPAIGN = {
 "hero-women": ("herow",10), "hero-men": ("r2herom",15), "seasonal-aw26": ("seasonal",0),
 "collection-evening": ("evening",2), "collection-resort": ("resort",5), "collection-signature": ("neutral",4),
 "collection-essentials": ("neutral",11), "collection-tailored": ("wblazer",2), "collection-seasonal": ("neutral",13),
 "editorial-noir": ("bw",1), "editorial-silk": ("scarf",0), "editorial-wool": ("fabric",1), "atelier": ("mtrouser",2),
}
def groups(path="/home/claude/elvare-luxury-fashion/photo-work/c.txt"):
    g, s = {}, None
    for l in open(path):
        l = l.strip()
        if l.startswith("@"): s = l[1:]; g[s] = []
        elif l: g[s].append(l.split("|"))
    return g
def resolve(group, idx, G=None):
    G = G or groups(); return G[group][idx]
