# Microsserviço de Bitcoin

API para gestão de investimentos em Bitcoin, com integração em tempo real de cotações.

## 🛠 Rotas Disponíveis
| Método | Rota                 | Descrição                       |
|--------|----------------------|---------------------------------|
| GET    | `/api/bitcoin`       | Listar todos os registros       |
| POST   | `/api/bitcoin`       | Adicionar nova compra           |
| PUT    | `/api/bitcoin/{id}`  | Editar registro                 |
| DELETE | `/api/bitcoin/{id}`  | Excluir registro                |

## 🐳 Execução com Docker
```bash
docker build -t bitcoin .
docker run -p 3005:3005 bitcoin


API Externa
Binance/CoinGecko: Cotação atualizada do BTC-BRL.

