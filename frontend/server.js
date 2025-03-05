const express = require('express');
const path = require('path');
const app = express();
const PORT = 3000;

// JSON ボディを扱うための設定
app.use(express.json());

// ルート最適化 API
app.post('/api/optimize', (req, res) => {
    // リクエストデータ例
    // const { latitude, longitude, departure, people, budget, days, startDate } = req.body;

    // ダミーの最適化ルートデータを返す
    const routeData = {
        route: [
            { lat: 35.681236, lng: 139.767125, name: "東京駅" },
            { lat: 35.689487, lng: 139.691711, name: "新宿" },
            { lat: 35.658034, lng: 139.701636, name: "渋谷" }
        ]
    };
    res.json(routeData);
});

// Viteの開発サーバでフロントを動かしたい場合は、特に静的ファイル配信は不要ですが、
// ビルド後の `dist` を使う場合は以下のように設定すればOK:
// app.use(express.static(path.join(__dirname, 'dist')));

app.listen(PORT, () => {
    console.log(`Server listening on port ${PORT}`);
});
