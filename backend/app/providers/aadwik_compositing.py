def build_composite(layers):
    required={"video","audio"}
    return {"valid":required.issubset(set(layers)),
            "layers":list(layers),
            "order":["video","color","titles","subtitles","audio"]}
