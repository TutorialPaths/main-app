from urllib.request import urlopen

inbuilt_defines = ["IMPORTS"]
groups = {}


def process(html, variables):
    try:
        try:
            html = html.decode()
        except Exception as e:
            html = html
        final = False
        dist = 0
        sets = []
        while not final:
            try:
                html.index('<!--$', dist)
            except ValueError:
                final = True
                break

            index = html.index('<!--$', dist)
            endindex = html.index('$-->', index)
            sets.append(html[index:endindex])
            dist = endindex

        for command in sets:
            start = 6
            middle = start + command[start:].index(' ')
            end = middle + command[middle:].index(']')

            comm = command[start:middle]
            key = command[middle + 1:end]

            if comm == "def":
                try:
                    inbuilt_defines.index(key)

                    if key == "IMPORTS":

                        children = command[end + 2:command.index('<![end')].split(',')
                        childobj = {}
                        for child in children:

                            start = child.index('@')
                            firstspace = child.index(' ', start)
                            secondspace = child.index(' ', firstspace + 2)

                            childname = child[start:firstspace]
                            childlocation = child[firstspace + 1:secondspace]
                            childtype = child[secondspace + 1:]

                            if childtype == 'auto':
                                if childlocation == 'auto:nav':

                                    nav = urlopen("https://dom.tutorialpaths.com/nav_static/_index.html").read().decode()

                                    html.replace("</head>", "<link rel='stylesheet' href='https://dom.tutorialpaths.com/nav/bundle.css'></head>")

                                elif childlocation == 'auto:nav_static':

                                    nav = urlopen("https://dom.tutorialpaths.com/nav/_index.html").read().decode()

                                    html.replace("</head>", "<link rel='stylesheet' href='https://dom.tutorialpaths.com/nav_static/bundle.css'></head>")

                                startcontent = html.index('<!--$[_CONTENT]-->')
                                endcontent = html.index('<!--[_CONTENT]$-->')
                                content = html[startcontent:endcontent].replace('<!--$[_CONTENT]-->', '')

                                beforecontent = html[:startcontent]
                                aftercontent = html[endcontent:].replace('<!--[_CONTENT]$-->', '')

                                html = beforecontent + nav.replace('<!--$[_CONTENT]$-->', content) + aftercontent

                                html = html.replace("@nav " + childlocation + " auto,", "")

                                return process(html, variables)

                            elif childtype == 'markedHTML':
                                if "DOM:" in childlocation:
                                    try:

                                        childobj[childname] = urlopen("https://dom.tutorialpaths.com/" + childlocation.replace("DOM:", "")).read().decode()
                                    except Exception as e:
                                        childobj[childname] = ""
                                else:
                                    try:
                                        childobj[childname] = variables[key]
                                    except KeyError:
                                        childobj[childname] = ""

                            elif childtype[:8] == 'markedJS':
                                commentstart = childtype[10:childtype.index("'", 10)]
                                commentend = childtype[13 + len(commentstart):childtype.index("'", 13 + len(commentstart))]
                                temporaryval = childtype.split("'")[len(childtype.split("'")) - 2]

                                childvalue = temporaryval

                                if "var:" in childlocation:
                                    try:
                                        childvalue = variables[childlocation.replace("var:", "")]
                                    except KeyError:
                                        childvalue = temporaryval
                                else:
                                    childvalue = temporaryval

                                html = html.replace(commentstart + "[import " + childname[1:] + "]" + commentend + temporaryval, childvalue)

                        groups[key] = childobj

                except ValueError:

                    children = command[end + 2:command.index('<![end')].split(',')
                    childobj = {}
                    for child in children:

                        start = child.index('@')
                        firstspace = child.index(' ', start)
                        secondspace = child.index(' ', firstspace + 2)

                        childname = child[start:firstspace]
                        childif = child[firstspace + 1:secondspace]
                        childcond = child[secondspace + 1:]

                        val = False
                        try:
                            val = variables[childcond.replace("\n", "").replace(" ", "")]
                        except KeyError:
                            val = False

                        check = bool(childif == "IF")
                        childobj[childname] = bool(val == check)

                    groups[key] = childobj

            elif comm == "start":
                group = groups[key.split("@")[0]]
                var = group["@" + key.split("@")[1]]

                if var:
                    html = html.replace("<!--$[start " + key + "]:", "")
                    html = html.replace("<![end " + key + "]$-->", "")
                else:
                    firsthalf = html[:html.index("<!--$[start " + key + "]:")]
                    secondhalf = html[html.index("<![end " + key + "]$-->") + len("<![end " + key + "]$-->"):]
                    html = firsthalf + secondhalf

            elif comm == "import":

                html = html.replace("<!--$[import " + key + "]$-->", groups["IMPORTS"]["@" + key])

        return html
    except Exception as e:
        return str(e)
