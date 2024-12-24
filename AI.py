from g4f.client import Client




class ChatGpt:
    @staticmethod
    def requestToAi(data):
        
        client = Client()
        with open('message_to_ai', encoding='utf8') as f:
            content = f.read()
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": content + data}],
        )
        return response.choices[0].message.content

 