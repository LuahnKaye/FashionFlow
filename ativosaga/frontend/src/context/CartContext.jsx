import React, { createContext, useState, useContext, useEffect, useCallback } from 'react';
import axios from 'axios';

const CartContext = createContext();

export const CartProvider = ({ children }) => {
  const [itens, setItens] = useState([]);

  const URL_PEDIDOS = "http://localhost:8001/pedidos";
  const URL_PAGAMENTOS = "http://localhost:8002"; // Removido /pagamentos que nao existe no backend

  // ... (outras funções)

  const realizarCheckout = async (token) => {
    try {
      if (itens.length === 0) return { sucesso: false, erro: "Carrinho vazio" };

      // 1. Criar o Pedido no backend
      const item = itens[0];
      const respostaPedido = await axios.post(URL_PEDIDOS + "/", {
        id_produto: item.id,
        quantidade: item.quantidade,
        preco_total: item.preco * item.quantidade
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });

      const pedidoCriado = respostaPedido.data;

      // 2. Criar Sessão no Stripe via Serviço de Pagamentos
      const respostaPagamento = await axios.post(URL_PAGAMENTOS + "/criar-checkout", {
        id_pedido: pedidoCriado.id,
        id_usuario: pedidoCriado.id_usuario,
        id_produto: item.id,
        nome_produto: item.nome,
        valor: item.preco * item.quantidade
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });

      // 3. Redirecionar para o Stripe
      window.location.href = respostaPagamento.data.url_checkout;
      return { sucesso: true };

    } catch (error) {
      console.error("Erro no checkout:", error);
      return { 
        sucesso: false, 
        erro: error.response?.data?.detail || "Erro ao processar pagamento." 
      };
    }
  };

  // Carrega o carrinho do localStorage ao iniciar
  useEffect(() => {
    const salvo = localStorage.getItem('ativosaga_carrinho');
    if (salvo) setItens(JSON.parse(salvo));
  }, []);

  // Salva no localStorage sempre que o carrinho mudar
  useEffect(() => {
    localStorage.setItem('ativosaga_carrinho', JSON.stringify(itens));
  }, [itens]);

  const adicionarAoCarrinho = (produto) => {
    setItens((atuais) => {
      const existe = atuais.find(item => item.id === produto.id);
      if (existe) {
        return atuais.map(item => 
          item.id === produto.id ? { ...item, quantidade: item.quantidade + 1 } : item
        );
      }
      return [...atuais, { ...produto, quantidade: 1 }];
    });
  };

  const atualizarQuantidade = (id, delta) => {
    setItens(atuais => atuais.map(item => {
      if (item.id === id) {
        const novaQtd = Math.max(1, item.quantidade + delta);
        return { ...item, quantidade: novaQtd };
      }
      return item;
    }));
  };

  const removerDoCarrinho = (id) => {
    setItens(atuais => atuais.filter(item => item.id !== id));
  };

  const limparCarrinho = useCallback(() => {
    setItens([]);
  }, []);

  const totalItens = itens.reduce((soma, item) => soma + item.quantidade, 0);
  const valorTotal = itens.reduce((soma, item) => soma + (item.preco * item.quantidade), 0);

  return (
    <CartContext.Provider value={{ 
      itens, 
      adicionarAoCarrinho, 
      removerDoCarrinho, 
      limparCarrinho, 
      totalItens, 
      valorTotal,
      realizarCheckout,
      atualizarQuantidade
    }}>
      {children}
    </CartContext.Provider>
  );
};

export const useCarrinho = () => useContext(CartContext);
