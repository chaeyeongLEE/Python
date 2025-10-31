// 초미니 프록시 서버 (검색만 제공)
const express = require("express");
const cors = require("cors");
const { Client } = require("@elastic/elasticsearch");



const app = express();
app.use(cors());
app.use(express.json());
app.disable("etag");                        // CHANGED
app.use((req, res, next) => {
    res.set("Cache-Control", "no-store");
    next();
});

const es = new Client({ node: "http://localhost:9200" });

app.get("/api/search", async (req, res) => { // CHANGED
                                             // --- Query Params ---
    const q = (req.query.q || "").trim();                   // CHANGED
    const brand = (req.query.brand || "").trim();
    const minPrice = Number(req.query.minPrice || "");
    const maxPrice = Number(req.query.maxPrice || "");
    const sort = (req.query.sort || "").trim();               // "price.asc" | "price.desc" | ""
    const page = Math.max(1, parseInt(req.query.page || "1", 10));
    const size = Math.min(50, Math.max(1, parseInt(req.query.size || "10", 10)));
    const from = (page - 1) * size;

    // --- ES Query ---
    const must = [];
    const filter = [];
    if (q) {
        must.push({ multi_match: { query: q, fields: ["name^2", "brand"] } }); // CHANGED
    }
    if (brand) filter.push({ term: { brand } });
    if (!Number.isNaN(minPrice) || !Number.isNaN(maxPrice)) {
        const range = {};
        if (!Number.isNaN(minPrice)) range.gte = minPrice;
        if (!Number.isNaN(maxPrice)) range.lte = maxPrice;
        filter.push({ range: { price: range } });
    }

    const sortClause =
        sort === "price.asc"  ? [{ price: "asc"  }] :
            sort === "price.desc" ? [{ price: "desc" }] :
                [{ _score: "desc" }];

    try {
        const r = await es.search({
            index: "products",
            from,
            size,
            query: must.length || filter.length
                ? { bool: { must: must.length ? must : [{ match_all: {} }], filter } }
                : { match_all: {} },                              // CHANGED
            sort: sortClause,
            highlight: q
                ? { fields: { name: {} }, pre_tags: ["<mark>"], post_tags: ["</mark>"] }
                : undefined,
        });

        const total = typeof r.hits.total === "object" ? r.hits.total.value : r.hits.total;
        const items = r.hits.hits.map((h) => ({
            id: h._id,
            score: h._score,
            ...h._source,
            nameHtml: h.highlight?.name?.[0] || null,           (하이라이트 결과)
        }));

        res.json({ ok: true, items, page, size, total });     // CHANGED
    } catch (e) {
        res.status(200).json({ ok: false, items: [], error: e.message }); // CHANGED
    }
});

app.listen(4000, () => console.log("API http://localhost:4000"));
