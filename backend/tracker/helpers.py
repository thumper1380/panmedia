def parse_accept_language(accept_language):
    languages = accept_language.split(",")
    lang_quality_list = []

    for lang in languages:
        parts = lang.split(";")
        if len(parts) == 2:
            # if quality is specified, use it
            lang_quality_list.append(
                (parts[0][:2].lower(), float(parts[1][2:])))
        else:
            # if no quality is specified, assume 1
            lang_quality_list.append((parts[0][:2].lower(), 1.0))

    # sort list by quality (highest first)
    lang_quality_list.sort(key=lambda x: x[1], reverse=True)

    # return language with highest quality
    return lang_quality_list[0][0]




