# Simulador de Investimentos - WordPress Elementor

Versão 2.0 - Compatível com WordPress 5.0+ e Elementor 3.0+

## Como Usar no WordPress Elementor

### Opção 1: Widget Custom HTML (Recomendado)

1. **Abra sua página no Elementor**
   - Vá para Elementor > Editar com Elementor

2. **Adicione um widget "Custom HTML"**
   - Clique em "+" para adicionar elemento
   - Procure por "Custom HTML"
   - Clique para adicionar

3. **Copie o código do simulador**
   - Abra o arquivo `simulador-investimentos.html`
   - **Copie APENAS a seção interna** (não precisa de <!DOCTYPE> etc):

   ```html
   <style>
   ... (todo o CSS) ...
   </style>

   <div class="sim-container">
   ... (todo o HTML) ...
   </div>

   <script>
   ... (todo o JavaScript) ...
   </script>
   ```

4. **Cole no widget**
   - Cole o código no campo de entrada do widget Custom HTML
   - Ajuste largura/altura conforme necessário

5. **Salve a página**
   - Clique em "Publicar" ou "Atualizar"

### Opção 2: Via Código (Tema Child)

Se quiser incorporar no tema:

1. Adicione ao `functions.php`:
```php
function enqueue_simulador() {
    wp_enqueue_script('chart-js', 'https://cdn.jsdelivr.net/npm/chart.js@3.9.1/dist/chart.min.js');
}
add_action('wp_enqueue_scripts', 'enqueue_simulador');
```

2. Crie um template ou use shortcode

## Compatibilidade

✅ **Testado com:**
- WordPress 5.0, 5.1, 5.2+ (até versão atual)
- Elementor 3.0, 3.1+ (até versão atual)
- Todos os navegadores modernos

✅ **Recursos Isolados:**
- CSS com prefixo `sim-` para evitar conflitos
- JavaScript em namespace `window.simuladorInvestimentos`
- Sem dependência de jQuery
- Chart.js carregado via CDN

## Troubleshooting

### "Script não carrega"
- Verifique se o widget está em "Custom HTML" e não em outro tipo
- Limpe o cache do WordPress (Elementor > Tools > Clear Cache)
- Verifique o console do navegador (F12) para erros

### "Estilos conflitando com o tema"
- Se o CSS do tema sobrescrever, aumente a especificidade
- Ou use o plugin "Custom CSS for Elementor"

### "Chart.js não encontrado"
- Verifique conexão com internet (CDN jsdelivr)
- Ou baixe Chart.js e hospede localmente

## Estrutura do Arquivo

```
simulador-investimentos.html
├── <style> - Dark mode CSS (prefixo sim-)
├── <body> - HTML semântico
│   ├── Header
│   ├── Formulário
│   └── Resultados (abas dinâmicas)
└── <script> - JavaScript vanilla (namespace protegido)
```

## Performance

- **Tamanho:** ~30 KB (gzip ~10 KB)
- **Dependências:** 0 (exceto Chart.js via CDN)
- **Compatibilidade:** IE11+ (moderno)

## Atualizações

Para atualizar o simulador:
1. Abra a página no Elementor
2. Clique no widget Custom HTML
3. Substitua o código completo
4. Salve

---

**Versão:** 2.0  
**Última atualização:** Jun 2026  
**Autor:** Seu Nome  
**Licença:** Livre para uso pessoal
