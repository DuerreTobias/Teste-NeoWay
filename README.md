# Teste-Neoway

Este script coleta informações sobre artistas, lançamentos e álbuns de música a partir da API Discogs. Os dados coletados incluem informações detalhadas sobre os artistas, seus membros, lançamentos de álbuns e detalhes de cada álbum (como título, ano, gêneros, estilos, rótulos e lista de faixas). O objetivo é consolidar essas informações e salvá-las em um arquivo JSONL.

## Funcionalidade

### O script realiza as seguintes etapas:

1. **Coleta de dados de artistas**: Para cada ID de artista fornecido, o script coleta informações gerais, como nome, nome real, membros (se houver) e URLs relacionadas.
2. **Coleta de lançamentos de álbuns**: O script busca os lançamentos do artista, limitando-se a coletar até 10 álbuns.
3. **Coleta de detalhes de álbuns**: Para cada lançamento, o script coleta detalhes sobre o álbum, incluindo título, ano, gêneros, estilos, rótulos e lista de faixas.
4. **Tratamento de erros**: O script lida com erros da API, incluindo o erro de limitação de requisições (código 429), realizando uma pausa antes de tentar novamente.
5. **Salvamento dos dados**: Os dados coletados são salvos em um arquivo JSONL para facilitar a leitura e manipulação posterior.

## Pré-requisitos

- **Python 3.x** instalado.
- **Bibliotecas Python**: `requests` (para interagir com a API Discogs).
  Para instalar as dependências, execute:
  ```bash
  pip install requests
  ```

## Como usar

1. **Substitua o token da API**: No código, a variável `Authorization` contém um token de acesso da API Discogs. Certifique-se de substituir o token de exemplo pelo seu próprio, obtido na sua conta do Discogs.

   Atenção: No caso deste teste, utilizei e deixei no codigo o token gerado pela minha própria conta, o qual deve ser suficiente para o uso. No entanto, caso ocorra algum problema, será necessário gerar e substituir por um novo token.

3. **IDs de artistas**: A lista `artist_ids` contém os IDs dos artistas cujos dados serão coletados. Você pode adicionar ou remover IDs conforme necessário.

4. **Execute o script**: Após configurar os parâmetros, execute o script em um ambiente Python:
   ```bash
   python3 Teste-Neoway.py
   ```

5. **Dados gerados**: Os dados serão salvos no arquivo `Dados Coletados.jsonl`, no mesmo diretório do script. Este arquivo contém os dados dos artistas, incluindo informações sobre seus álbuns e faixas.

## Funções principais

### `fazer_requisicao(url, headers)`
- Realiza uma requisição HTTP à API Discogs e lida com erros de limitação (código 429), aguardando 5 segundos antes de tentar novamente.

### `obter_informacoes_artista(artist_id, fazer_requisicao_func)`
- Coleta informações gerais sobre um artista, incluindo nome, membros e URLs.

### `obter_lancamentos_artista(artist_id, fazer_requisicao_func)`
- Coleta os lançamentos do artista, retornando uma lista de álbuns.

### `obter_detalhes_album(release_id, fazer_requisicao_func)`
- Coleta informações detalhadas sobre um álbum, incluindo título, ano, gêneros, estilos, rótulos e faixas.

### `coletar_e_salvar_dados(artist_id, lista_dados_artistas, fazer_requisicao_func)`
- Coleta os dados completos do artista e seus álbuns e os armazena em um formato estruturado.

### `processar_dados(artist_ids, fazer_requisicao_func)`
- Processa a coleta de dados para uma lista de IDs de artistas, chamando as funções anteriores para coletar e salvar os dados.

### `salvar_dados_no_arquivo(lista_dados_artistas, nome_arquivo)`
- Salva os dados coletados em um arquivo JSONL para persistência.

## Exemplos de uso

### Exemplo de dados de saída

O arquivo JSONL gerado terá uma estrutura semelhante a esta para cada artista:

```json
{
  "id": 40029,
  "name": "Nome do Artista",
  "real_name": "Nome Real",
  "members": [
    {
      "name": "Membro 1",
      "id": 12345
    }
  ],
  "urls": [
    "https://www.example.com"
  ],
  "albums": [
    {
      "id": 1234567,
      "title": "Álbum 1",
      "year": 2020,
      "genres": ["Rock", "Indie"],
      "styles": ["Alternative"],
      "labels": [
        {
          "name": "Label 1",
          "id": 7654321
        }
      ],
      "tracklist": [
        {
          "position": "1",
          "title": "Faixa 1",
          "duration": "3:45"
        }
      ]
    }
  ],
  "grouped_ids": {
    "member_ids": [12345],
    "album_ids": [1234567],
    "label_ids": [7654321]
  }
}
```

### Limitações

- O script atualmente coleta até 10 álbuns por artista. Para coletar mais, basta ajustar a variável `contador_albuns`.
- A API do Discogs pode limitar o número de requisições, e o script lida com isso automaticamente, aguardando antes de tentar novamente.
