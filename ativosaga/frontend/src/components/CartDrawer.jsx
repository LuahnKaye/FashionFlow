import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Trash2, CreditCard, Loader2, AlertCircle, Plus, Minus } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useCarrinho } from '../context/CartContext';
import { useAuth } from '../context/AuthContext';

export default function CartDrawer({ isOpen, onClose }) {
  const { itens, removerDoCarrinho, valorTotal, totalItens, realizarCheckout, atualizarQuantidade } = useCarrinho();
  const { usuario } = useAuth();
  const [carregando, setCarregando] = useState(false);
  const [erro, setErro] = useState('');
  const navigate = useNavigate();

  const handleFinalizar = async () => {
    if (!usuario) {
      navigate('/login');
      onClose();
      return;
    }

    setCarregando(true);
    setErro('');

    // Pegamos o token do localStorage (salvo pelo AuthContext)
    const token = localStorage.getItem('ativosaga_token');
    const resultado = await realizarCheckout(token);

    if (!resultado.sucesso) {
      setErro(resultado.erro);
      setCarregando(false);
    }
    // Se sucesso, o navegador sera redirecionado pela funcao realizarCheckout
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 bg-black/60 backdrop-blur-sm z-[60]"
          />

          <motion.div 
            initial={{ x: '100%' }}
            animate={{ x: 0 }}
            exit={{ x: '100%' }}
            transition={{ type: 'spring', damping: 25, stiffness: 200 }}
            className="fixed right-0 top-0 h-full w-full max-w-md bg-segunda border-l border-white/10 z-[70] p-8 flex flex-col shadow-[-20px_0_50px_rgba(0,0,0,0.5)]"
          >
            <div className="flex justify-between items-center mb-10">
              <h2 className="text-2xl font-display font-bold">Seu Carrinho ({totalItens})</h2>
              <button onClick={onClose} className="p-2 hover:bg-white/10 rounded-full transition-colors">
                <X className="w-6 h-6" />
              </button>
            </div>

            {erro && (
              <div className="bg-red-500/10 border border-red-500/20 text-red-500 p-4 rounded-xl mb-6 flex items-center gap-3 text-sm">
                <AlertCircle className="w-5 h-5 flex-shrink-0" />
                {erro}
              </div>
            )}

            <div className="flex-1 overflow-y-auto space-y-6 pr-2 custom-scrollbar">
              {itens.length === 0 ? (
                <div className="h-full flex flex-col items-center justify-center text-texto-secundario opacity-50 text-center">
                  <p>Seu carrinho está vazio.</p>
                  <p className="text-xs mt-2">Adicione ativos digitais para continuar.</p>
                </div>
              ) : (
                itens.map((item) => (
                  <div key={item.id} className="flex gap-4 group">
                    <div className="w-20 h-24 bg-white/5 rounded-xl flex items-center justify-center text-[10px] italic text-white/20 overflow-hidden border border-white/5">
                      {item.id}
                    </div>
                    <div className="flex-1">
                      <h4 className="font-semibold text-lg">{item.nome}</h4>
                      <div className="flex items-center gap-3 mt-2">
                        {item.quantidade > 1 ? (
                          <button 
                            onClick={() => atualizarQuantidade(item.id, -1)}
                            className="w-6 h-6 flex items-center justify-center border border-white/10 rounded-full hover:bg-white/10 transition-colors"
                          >
                            <Minus className="w-3 h-3" />
                          </button>
                        ) : (
                          <button 
                            onClick={() => removerDoCarrinho(item.id)}
                            className="w-6 h-6 flex items-center justify-center border border-red-500/20 rounded-full hover:bg-red-500/10 text-red-500 transition-colors"
                          >
                            <Trash2 className="w-3 h-3" />
                          </button>
                        )}
                        <span className="text-sm font-bold w-4 text-center">{item.quantidade}</span>
                        <button 
                          onClick={() => atualizarQuantidade(item.id, 1)}
                          className="w-6 h-6 flex items-center justify-center border border-white/10 rounded-full hover:bg-white/10 transition-colors"
                        >
                          <Plus className="w-3 h-3" />
                        </button>
                      </div>
                      <p className="text-destaque font-bold mt-1">R$ {(item.preco * item.quantidade).toFixed(2)}</p>
                    </div>
                    <button 
                      onClick={() => removerDoCarrinho(item.id)}
                      className="opacity-0 group-hover:opacity-100 p-2 text-white/30 hover:text-red-500 transition-all"
                    >
                      <X className="w-4 h-4" />
                    </button>
                  </div>
                ))
              )}
            </div>

            {itens.length > 0 && (
              <div className="mt-8 pt-8 border-t border-white/10 space-y-6">
                <div className="flex justify-between items-end">
                  <span className="text-texto-secundario uppercase tracking-widest text-xs font-bold">Total</span>
                  <span className="text-3xl font-display font-bold">R$ {valorTotal.toFixed(2)}</span>
                </div>
                
                <button 
                  onClick={handleFinalizar}
                  disabled={carregando}
                  className="w-full bg-white text-black py-5 rounded-2xl font-bold flex items-center justify-center gap-3 hover:scale-[1.02] active:scale-[0.98] transition-all disabled:opacity-50"
                >
                  {carregando ? (
                    <>Processando <Loader2 className="w-5 h-5 animate-spin" /></>
                  ) : (
                    <>Pagar R$ {valorTotal.toFixed(2)} <CreditCard className="w-5 h-5" /></>
                  )}
                </button>
                <p className="text-[10px] text-center text-texto-secundario uppercase tracking-tighter">
                  {usuario ? `Comprando como ${usuario.nome}` : 'Faça login para finalizar'}
                </p>
              </div>
            )}
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
