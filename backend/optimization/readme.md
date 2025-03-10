# 概要
貪欲に、予算と時間の範囲内でできる限り多くの観光地を回る旅行プランを作成するプログラム。
観光地のデータはdataディレクトリにあるjsonファイルから読み込む。

# 使い方
## 入力
```
python get_optimal_travel.py <departure time(00:00)> <city> <budget> <days>
```
<departure  time> 出発時間。(00:00形式) (ex. 09:00, 12:00)
<city> 観光する都市の名称。現在対応しているのは"hakodate", "kobe", "hiroshima"のみ(ex. hakodate)
<budget> 予算。(ex. 10000, 70000)
<days> 旅行日数。(ex. 1, 2, 3)



## 出力
[
	[
		{
		"destination_id": (観光地のID),
		"visit_cost": (観光費。入場料金など。),
		"travel_cost": (移動費。飛行機の場合は飛行機代金。バスの場合はバス代金。徒歩の場合は0),
		"visit_time": (観光時間。分単位),
		"travel_time":  (移動時間。分単位),
		"total_cost": (visit_cost + travel_cost),
		"arrival_time": (出発してからその観光地に到着する時間),
		"transportation_method": (飛行機 or バス or 徒歩 or 電車)
		},
		...
	],
	[
		(2日目の旅行プラン),
	],
]



```

# 例
```
$ python3 get_optimal_travel.py 09:00 hakodate 70000 2
[
  [
    {
      "destination_id": 264,
      "visit_cost": 0,
      "travel_cost": 10500,
      "visit_time": 60,
      "travel_time": 120,
      "total_cost": 10500,
      "arrival_time": 120,
      "transportation_method": "飛行機"
    },
    {
      "destination_id": 235,
      "visit_cost": 900,
      "travel_cost": 200,
      "visit_time": 60,
      "travel_time": 40,
      "total_cost": 1100,
      "arrival_time": 220,
      "transportation_method": "バス"
    },
    {
      "destination_id": 236,
      "visit_cost": 0,
      "travel_cost": 0,
      "visit_time": 60,
      "travel_time": 10,
      "total_cost": 0,
      "arrival_time": 290,
      "transportation_method": "徒歩"
    },
    {
      "destination_id": 237,
      "visit_cost": 0,
      "travel_cost": 0,
      "visit_time": 120,
      "travel_time": 5,
      "total_cost": 0,
      "arrival_time": 355,
      "transportation_method": "徒歩"
    },
    {
      "destination_id": 217,
      "visit_cost": 3000,
      "travel_cost": 200,
      "visit_time": 180,
      "travel_time": 40,
      "total_cost": 3200,
      "arrival_time": 515,
      "transportation_method": "バス"
    },
    {
      "destination_id": 284,
      "visit_cost": 9000,
      "travel_cost": 200,
      "travel_time": 10,
      "total_cost": 9200,
      "arrival_time": 705,
      "transportation_method": "バス"
    }
  ],
  [
    {
      "destination_id": 244,
      "visit_cost": 500,
      "travel_cost": 200,
      "visit_time": 60,
      "travel_time": 15,
      "total_cost": 700,
      "arrival_time": 15,
      "transportation_method": "バス"
    },
    {
      "destination_id": 222,
      "visit_cost": 500,
      "travel_cost": 200,
      "visit_time": 60,
      "travel_time": 30,
      "total_cost": 700,
      "arrival_time": 105,
      "transportation_method": "バス"
    },
    {
      "destination_id": 215,
      "visit_cost": 0,
      "travel_cost": 0,
      "visit_time": 120,
      "travel_time": 10,
      "total_cost": 0,
      "arrival_time": 175,
      "transportation_method": "徒歩"
    },
    {
      "destination_id": 210,
      "visit_cost": 1500,
      "travel_cost": 200,
      "visit_time": 60,
      "travel_time": 20,
      "total_cost": 1700,
      "arrival_time": 315,
      "transportation_method": "バス"
    },
    {
      "destination_id": 233,
      "visit_cost": 200,
      "travel_cost": 0,
      "visit_time": 60,
      "travel_time": 10,
      "total_cost": 200,
      "arrival_time": 385,
      "transportation_method": "徒歩"
    },
    {
      "destination_id": 232,
      "visit_cost": 1000,
      "travel_cost": 0,
      "visit_time": 120,
      "travel_time": 15,
      "total_cost": 1000,
      "arrival_time": 460,
      "transportation_method": "徒歩"
    },
    {
      "destination_id": 0,
      "visit_cost": 0,
      "travel_cost": 19000,
      "travel_time": 120,
      "total_cost": 19000,
      "arrival_time": 700,
      "transportation_method": "飛行機"
    }
  ]
]

$ python3 get_optimal_travel.py 09:00 hakodate 10000 2
[
  [],
  []
]

旅程が見つからない場合は、空のリストが返される。

```


# メモ
本質部分は plan_itinerary関数にあるので、バックエンドにはその関数とその上にある要素をコピペして持っていっても良いかもしれない。
現在はdataディレクトリにあるデータから読み出すような仕様となっている。DBからの読み込み速度などを考えると、このプログラムに関しては本番環境もdataディレクトリから読み込む形で良いと考えている。
