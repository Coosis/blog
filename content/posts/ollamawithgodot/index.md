---
title: "Use Ollama with Godot"
date: 2023-12-08T15:50:38+08:00
draft: false
---

# Intro to Ollama:
I found a open source project: [ollama](https://ollama.ai/) by jmorganca. Github page:[Ollama](https://github.com/jmorganca/ollama). Ollama lets you host language models and open up endpoints for other programs to use. The models are mainly open-sourced models like [llama2](https://ai.meta.com/llama/) from [Meta AI](https://ai.meta.com/). Now all open-ai-privately-owns-its-models-for-profits nonsense aside, this got me very excited. Imagine a game where every NPC is able to produce dialogs by themselves, and we're able to have a real conversation with them. Ask about the game world, or about their lives, and get actual response. How amazing is that?

# Mechanism:
The [API docs](https://github.com/jmorganca/ollama/blob/main/docs/api.md) at ollama site is very clear and instructive. After following it I was able to set up a model running on my macbook. Then I opened up godot. Now, to interact with the model, you send a httprequest to the endpoint with your query information using .json files, and a response will be generated back to you, in .json format. Visit [API docs](https://github.com/jmorganca/ollama/blob/main/docs/api.md) to see list of all possible parameters in the query. 

# Doing it... badly:
In godot, http requests are made easy with the use of httprequest nodes. They have a signal called request_conpleted, which will emit when the http request is finished, that is, when the full response is received. This is what I did at first. I used `JSON.stringify()` to create a json object for query, send the json on the click of a button, and handled the response using something like `json.parse(body.get_string_from_utf8())`. This worked, and I was very excited about it, but it soon hit me: this is not ideal, as the response can only show when the entire process is finished. When using models like copilot chat and chatgpt and bard, the response is extended bit by bit. I wanted to achieve a similar effect. But if anyone is curious about the original code, here's that:
```
#Used when button is clicked
func legacy():
	var http_request = $HTTPRequest  # Reference to your HTTPRequest node

	var body = JSON.stringify({
		"model": "llama2",
		"prompt": textbud.text,
		"stream": false
	})
	
	http_request.request(websocket_url, [], HTTPClient.METHOD_POST, body)

#Connected to the signal mentioned
func _on_http_request_request_completed(result, response_code, headers, body):
	var json = JSON.new()
	json.parse(body.get_string_from_utf8())
	var response = json.get_data()
	print(response["response"])
	lab.text = response["response"]
```

# Doing it:
After looking through the documentation for godot 4, I quickly found out that using httprequest nodes is not going to cut it. The httprequest nodes are build from HTTPClient, therefore I have to implement from HTTPClient. I needed to handle connection, polling, status-checking and data-retriving. Here's the code:
Side note: I wrote this in the script of a HBoxContainer to make it easier to show the response.
```
extends HBoxContainer

@onready var textbud = $TextEdit
@onready var lab = $Label

# The URL we will connect to
var websocket_url = "http://localhost:11434/api/generate"
var err = 0
var client # Create the Client.
var connected = false

# Called when the node enters the scene tree for the first time.
func _ready():
	client = HTTPClient.new()
	err = client.connect_to_host("http://localhost", 11434)
	assert(err == OK)

# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta):
	client.poll()
	if(client.get_status() == HTTPClient.STATUS_CONNECTING or client.get_status() == HTTPClient.STATUS_RESOLVING):
		if(!connected):
			print("Connecting...")
	elif(client.get_status() == HTTPClient.STATUS_CONNECTED):
		if(!connected):
			connected = true
			print("Connected!")
	elif(client.get_status() == HTTPClient.STATUS_DISCONNECTED):
		if(connected):
			connected = false
			print("Disconnected!")
	elif(client.get_status() == HTTPClient.STATUS_BODY):
		print("Requesting...")
		if(client.has_response()):
			var chunk = client.read_response_body_chunk()
			var jsdata = JSON.new()
			jsdata.parse(chunk.get_string_from_utf8())
			var data = jsdata.get_data()
			if(data != null):
				print(data["response"])
				lab.text += data["response"]

func _on_button_pressed():
	var query_string = JSON.stringify({
		"model": "llama2",
		"prompt": textbud.text,
		"stream": true
	})
	var headers = ["Content-Type: application/x-www-form-urlencoded", "Content-Length: " + str(query_string.length())]
	var result = client.request(HTTPClient.METHOD_POST, "/api/generate", [], query_string)
```

# Result:
{{< gallery caption-effect="fade" >}}
    {{< figure src="posts/ollamawithgodot/res1.png" link="posts/ollamawithgodot/res1.png" caption="Result 1" >}}
    {{< figure src="posts/ollamawithgodot/res2.png" link="posts/ollamawithgodot/res2.png" caption="Result 2" >}}
    {{< figure src="posts/ollamawithgodot/res2.png" link="posts/ollamawithgodot/res2.png" caption="Result 3" >}}
{{< /gallery >}}
