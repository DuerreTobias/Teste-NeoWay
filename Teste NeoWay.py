import json
import requests
import time

# Lista de IDs dos artistas
artist_ids = [40029, 45467, 110593, 84752, 170355, 57103, 81013, 153073, 82730, 251595]
base_url = "https://api.discogs.com"
headers = {
    "User-Agent": "DiscogsDataCollector/1.0",
    "Authorization": "Discogs token=fDdbOxMxztGQWSdWinOjyinFZbWiHuOdJwexZRJJ"  # Substitua pelo seu token se disponível
}


# Função para lidar com requisições e tratamento de erro 429
def fazer_requisicao(url, headers):
    while True:
        resposta = requests.get(url, headers=headers)
        if resposta.status_code == 429:
            print("Limite de requisições atingido. Aguardando antes de tentar novamente...")
            time.sleep(5)  # Aguarde 5 segundos antes de tentar novamente
        else:
            return resposta


# Função para buscar informações do artista
def obter_informacoes_artista(artist_id, fazer_requisicao_func):
    url = f"{base_url}/artists/{artist_id}"
    resposta = fazer_requisicao_func(url, headers)
    if resposta.status_code == 200:
        return resposta.json()
    else:
        print(f"Erro ao buscar informações do artista {artist_id}: {resposta.status_code}")
        return {}


# Função para buscar lançamentos do artista
def obter_lancamentos_artista(artist_id, fazer_requisicao_func):
    url = f"{base_url}/artists/{artist_id}/releases"
    resposta = fazer_requisicao_func(url, headers)
    if resposta.status_code == 200:
        return resposta.json()
    else:
        print(f"Erro ao buscar lançamentos do artista {artist_id}: {resposta.status_code}")
        return {}


# Função para buscar detalhes de um álbum
def obter_detalhes_album(release_id, fazer_requisicao_func):
    url = f"{base_url}/releases/{release_id}"
    resposta = fazer_requisicao_func(url, headers)
    
    if resposta.status_code == 200:
        return resposta.json()
    elif resposta.status_code == 404:
        print(f"Álbum {release_id} não encontrado (Erro 404). Pulando álbum.")
        return None
    else:
        print(f"Erro ao buscar detalhes do álbum {release_id}: {resposta.status_code}")
        return None


# Função principal para coletar e salvar os dados em JSON
def coletar_e_salvar_dados(artist_id, lista_dados_artistas, fazer_requisicao_func):
    albuns_processados = set()  # Evitar duplicados
    contador_albuns = 0  # Contador de álbuns processados
    
    # Coletando os dados do artista
    informacoes_artista = obter_informacoes_artista(artist_id, fazer_requisicao_func)
    if informacoes_artista:  # Verifica se os dados foram retornados com sucesso
        dados_artista = {
            "id": informacoes_artista.get("id"),
            "name": informacoes_artista.get("name", "Não disponível"),
            "real_name": informacoes_artista.get("realname", "Não disponível"),
            "members": [
                {"name": membro.get("name", "Não disponível"), "id": membro.get("id", "Não disponível")}
                for membro in informacoes_artista.get("members", [])
            ] if "members" in informacoes_artista else None,
            "urls": informacoes_artista.get("urls", []),
            "albums": [],  # Lista para armazenar os álbuns do artista
            "grouped_ids": {
                "member_ids": [membro.get("id") for membro in informacoes_artista.get("members", [])],
                "album_ids": [],
                "label_ids": []
            }  # Agrupar IDs
        }

        # Buscando lançamentos do artista
        lancamentos = obter_lancamentos_artista(artist_id, fazer_requisicao_func)
        if lancamentos:  # Verifica se os lançamentos foram retornados com sucesso
            for lancamento in lancamentos.get("releases", []):
                if contador_albuns >= 10:  # Limita a coleta de álbuns a 10
                    break
                if lancamento["type"] == "release" and lancamento["id"] not in albuns_processados:
                    album_id = lancamento["id"]
                    detalhes_album = obter_detalhes_album(album_id, fazer_requisicao_func)

                    if detalhes_album:
                        dados_album = {
                            "id": detalhes_album.get("id"),
                            "title": detalhes_album.get("title", "Não disponível"),
                            "year": detalhes_album.get("year", "Não disponível"),
                            "genres": detalhes_album.get("genres", []),
                            "styles": detalhes_album.get("styles", []),
                            "labels": [
                                {
                                    "name": label.get("name", "Não disponível"),
                                    "id": label.get("id", "Não disponível")
                                }
                                for label in detalhes_album.get("labels", [])
                            ],
                            "tracklist": [
                                {
                                    "position": track.get("position", "Não disponível"),
                                    "title": track.get("title", "Não disponível"),
                                    "duration": track.get("duration", "Não disponível")
                                }
                                for track in detalhes_album.get("tracklist", [])
                            ]
                        }
                        dados_artista["albums"].append(dados_album)  # Adiciona álbum à lista de álbuns do artista
                        dados_artista["grouped_ids"]["album_ids"].append(dados_album["id"])  # Agrupa IDs de álbuns
                        
                        # Agrupar IDs de rótulos
                        for label in detalhes_album.get("labels", []):
                            dados_artista["grouped_ids"]["label_ids"].append(label.get("id"))
                        
                        # Marcar o álbum como processado
                        albuns_processados.add(album_id)
                        contador_albuns += 1  # Incrementa o contador de álbuns

        lista_dados_artistas.append(dados_artista)


# Função que chama a função de coleta de dados para cada artista
def processar_dados(artist_ids, fazer_requisicao_func):
    lista_dados_artistas = []  # Lista para armazenar os dados dos artistas com os álbuns embutidos

    for artist_id in artist_ids:
        print(f"Coletando dados para o artista ID {artist_id}...")
        coletar_e_salvar_dados(artist_id, lista_dados_artistas, fazer_requisicao_func)
        print(f"Dados do artista ID {artist_id} processados.")

    return lista_dados_artistas


# Função para salvar os dados no arquivo
def salvar_dados_no_arquivo(lista_dados_artistas, nome_arquivo):
    with open(nome_arquivo, "w", encoding="utf-8") as jsonl_file:
        for dados_artista in lista_dados_artistas:
            # Salvando com indentação para melhorar legibilidade
            jsonl_file.write(json.dumps(dados_artista, ensure_ascii=False, indent=2) + "\n")
    print(f"Todos os dados foram salvos em {nome_arquivo}.")


# Consolidação dos dados
output_file = "Dados Coletados.jsonl"
dados_artistas = processar_dados(artist_ids, fazer_requisicao)
salvar_dados_no_arquivo(dados_artistas, output_file)
