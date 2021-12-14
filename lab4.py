import tkinter

from bs4 import BeautifulSoup
import requests
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt


def url_is_good(given_url):
    if (given_url is None or len(given_url) < 2 or
            given_url.find('#') != -1 or
            given_url.find('.mp3') != -1 or
            given_url.find('.jpg') != -1 or
            given_url.find('.php') != -1 or
            given_url.find('javascript') != -1):
        return False
    else:
        return True


def make_valid_url_string(link):
    global main_pg
    if not url_is_good(link):
        return '0'
    else:
        if link.find('http:') != -1 or link.find('https:') != -1:
            pass
        else:
            if link.find(main_pg) != -1:
                pass
            else:
                return main_pg + link
    return link


def get_to_pgs(from_pg, relationships_list):
    to_pgs = set()
    for row in relationships_list:
        if row[0] == from_pg:
            to_pgs.add(row[1])
    if len(to_pgs) == 0:
        to_pgs.add("")
    return to_pgs


def get_ranks_dict(relationships_list):
    links = set()
    ranks = {}
    for row in relationships_list:
        links.add(row[0])
        links.add(row[1])
    for link in links:
        ranks[link] = 1.0
    for i in range(100):
        for link in links:
            from_pgs = set()
            for row in relationships_list:
                if row[1] == link:
                    from_pgs.add(row[0])
            ranks_sum = sum(
                (float(ranks[node]) / len(get_to_pgs(node, relationships_list))) for node in from_pgs)
            ranks[link] = 0.4 / len(links) + (1 - 0.4) * ranks_sum # 0.4 - d (коеф. затухання)
    ranks_sum = sum(ranks.values())
    for page in ranks.keys():
        ranks[page] /= ranks_sum
    return dict(sorted(ranks.items(), key=lambda item: item[1], reverse=True))


def run_op():
    global main_pg
    main_pg = main_page_enter.get()
    soup = BeautifulSoup(requests.get(main_pg).content, "html.parser")
    links = []
    for line in soup.find_all('a'):
        if len(links) < 4:
            href = line.get('href')
            links.append([main_pg, href])
        else:
            break
    links_number = 0
    for i in range(4):
        start_link = links_number
        end_pos = len(links)
        for i in range(start_link, end_pos):
            limit = 3
            if not make_valid_url_string(links[i][1]) == "0":
                soup = BeautifulSoup(requests.get(make_valid_url_string(links[i][1])).content, "html.parser")
                count = 0
                for line in soup.find_all('a'):
                    if count < limit:
                        href = line.get('href')
                        if href is not None:
                            links.append([links[i][1], href])
                            count += 1
                    else:
                        break
                links_number += 1

    dataframe = pd.DataFrame(links, columns=["from", "to"])
    graph = nx.from_pandas_edgelist(dataframe, 'from', 'to', create_using=nx.DiGraph(length=50))
    ranks = get_ranks_dict(links)
    top_ten_links = ''
    for link in list(ranks.items())[:10]:
        top_ten_links += str(link)[1:-1] + "\n"
    result_lbl.config(text=top_ten_links)
    d = dict(graph.degree)
    nx.draw(graph, with_labels=False, node_size=[d[k] * 60 for k in d], node_color="purple", alpha=0.1, arrows=True,
            pos=nx.spring_layout(graph)) #добавление в граф
    plt.show()


master = tkinter.Tk()
main_pg = ''
main_page_enter = tkinter.Entry(master, width=70)
main_page_enter.grid(row=0, column=0)
run_btn = tkinter.Button(master, text='Run', command=run_op)
run_btn.grid(row=0, column=1)
result_lbl = tkinter.Label(master)
result_lbl.grid(row=1, column=0)
master.mainloop()
