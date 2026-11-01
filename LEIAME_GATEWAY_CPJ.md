# LEIA-ME — Gateway CPJ (Flask + Cloudflare Tunnel)

## Para que serve
O `gateway.py` roda uma API Flask na porta 5000 e consulta o MySQL CPJ.
O Cloudflare Tunnel cria um endereço HTTPS temporário para o PortalCliente acessar essa API.

**Importante:** o endereço `trycloudflare.com` é temporário. Se o túnel for encerrado/recriado, o endereço pode mudar e você precisa atualizar `CPJ_GATEWAY_URL` no `.env` do Django.

## Como iniciar manualmente

### 1. Iniciar o Gateway Flask
No computador onde está o arquivo `C:\gateway_cpj\gateway.py`:

1. Abra o VS Code na pasta `C:\gateway_cpj`.
2. Abra um terminal.
3. Execute:

```powershell
C:\Users\Administ\AppData\Local\Programs\Python\Python310\python.exe C:\gateway_cpj\gateway.py
```

4. Deixe esse terminal aberto. O Flask precisa continuar rodando na porta 5000.

Teste local no navegador:
`http://127.0.0.1:5000/teste-cpj`

O esperado é um JSON com `status: ok` e `resultado: 1`.

### 2. Iniciar o Cloudflare Tunnel
Abra **outro terminal** no mesmo computador. Não feche o terminal do Flask.

Execute:

```powershell
cloudflared tunnel --url http://localhost:5000
```

Aguarde aparecer uma linha semelhante a:

```text
Your quick Tunnel has been created! Visit it at:
https://NOME-ALEATORIO.trycloudflare.com
```

Copie o endereço HTTPS completo que aparecer. Não use o endereço antigo: o nome pode mudar a cada nova execução.

### 3. Atualizar o PortalCliente
Abra o arquivo `.env` na pasta principal do projeto Django `PortalCliente` e ajuste a variável:

```env
CPJ_GATEWAY_URL=https://NOME-ALEATORIO.trycloudflare.com
```

Substitua `https://NOME-ALEATORIO.trycloudflare.com` pelo endereço novo exibido no terminal do `cloudflared`. Não coloque `/consulta` no final.

Salve o `.env`. Reinicie o processo Django/servidor web para garantir que ele carregue a variável atualizada.

### 4. Testar o túnel
No navegador, abra:

`https://NOME-ALEATORIO.trycloudflare.com/teste-cpj`

Troque o endereço pelo que acabou de ser gerado. O esperado é:

```json
{
  "status": "ok",
  "resultado": 1
}
```

Depois, teste a rota do Django:
`/teste-gateway/`

Use o domínio e caminho normais do seu PortalCliente, por exemplo:
`https://SEU-DOMINIO/teste-gateway/`

## Se parar de funcionar
- Se o terminal do Flask fechar, inicie novamente o `gateway.py`.
- Se o terminal do `cloudflared` fechar, execute novamente o comando do passo 2.
- Se o túnel for recriado e gerar outro endereço, atualize `CPJ_GATEWAY_URL` no `.env` e reinicie o Django.
- Se aparecer `DNS_PROBE_FINISHED_NXDOMAIN`, o endereço pode ter expirado ou estar digitado incorretamente; gere um túnel novo e atualize o `.env`.
- Se aparecer erro 502, confira se o Flask ainda está rodando em `localhost:5000`.

## Atenção à segurança
Este procedimento usa um Quick Tunnel temporário, útil para testes, mas não é uma configuração de produção.
O endpoint `/consulta` aceita SQL enviado na requisição. Não deixe essa API exposta publicamente sem autenticação, restrição das consultas permitidas e permissões de leitura limitadas no MySQL. Não compartilhe credenciais nem coloque senhas neste arquivo LEIA-ME.
