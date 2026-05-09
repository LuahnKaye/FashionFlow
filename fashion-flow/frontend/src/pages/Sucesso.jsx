import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { CheckCircle, ArrowRight, Download, Loader2, AlertCircle, RefreshCcw } from 'lucide-react';
import { Link, useSearchParams } from 'react-router-dom';
import axios from 'axios';
import { useCarrinho } from '../context/CartContext';

export default function Sucesso() {
  const [params] = useSearchParams();
  const id_sessao = params.get('sessao_id');
  const { limparCarrinho } = useCarrinho();
  const [verificando, setVerificando] = useState(true);
  const [status, setStatus] = useState("pendente"); // "sucesso", "pendente", "erro"

  const verificarPagamento = () => {
    if (id_sessao) {
      setVerificando(true);
      axios.get(`http://localhost:8002/confirmar-pagamento/${id_sessao}`)
        .then(res => {
          console.log("Resposta do servidor:", res.data);
          if (res.data.status === "PAGO") {
            setStatus("sucesso");
            limparCarrinho();
          } else {
            setStatus("pendente");
          }
          setVerificando(false);
        })
        .catch(err => {
          console.error("Erro ao verificar:", err);
          setStatus("erro");
          setVerificando(false);
        });
    }
  };

  useEffect(() => {
    verificarPagamento();
  }, [id_sessao]);

  if (verificando) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center text-white bg-black">
        <Loader2 className="w-12 h-12 animate-spin text-destaque mb-4" />
        <p className="text-texto-secundario animate-pulse">Sincronizando com o Stripe...</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center px-4 pt-20">
      <div className="absolute top-0 left-0 w-full h-full -z-10 bg-[radial-gradient(circle_at_50%_50%,#0a1a0a_0%,#000000_100%)]" />
      
      <motion.div 
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        className="vidro w-full max-w-2xl p-12 rounded-[3rem] shadow-2xl text-center border-white/10"
      >
        {status === "sucesso" ? (
          <>
            <div className="w-24 h-24 bg-green-500 rounded-full flex items-center justify-center mx-auto mb-8 shadow-[0_0_50px_rgba(34,197,94,0.4)]">
              <CheckCircle className="w-12 h-12 text-black" />
            </div>
            <h1 className="text-4xl font-display font-bold mb-4">Pagamento Confirmado!</h1>
            <p className="text-texto-secundario text-lg mb-10">
              Seu ativo digital foi liberado. Divirta-se com sua nova aquisição!
            </p>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Link to="/" className="flex items-center justify-center gap-2 bg-white text-black py-4 rounded-2xl font-bold">
                Voltar à Loja <ArrowRight className="w-5 h-5" />
              </Link>
              <Link to="/galeria" className="flex items-center justify-center gap-2 bg-destaque text-black py-4 rounded-2xl font-bold">
                Acessar Galeria <Download className="w-5 h-5" />
              </Link>
            </div>
          </>
        ) : (
          <>
            <div className="w-24 h-24 bg-yellow-500/20 rounded-full flex items-center justify-center mx-auto mb-8 border border-yellow-500/50">
              <AlertCircle className="w-12 h-12 text-yellow-500" />
            </div>
            <h1 className="text-4xl font-display font-bold mb-4">Aguardando Confirmação</h1>
            <p className="text-texto-secundario text-lg mb-10">
              O Stripe ainda está processando seu pagamento. Isso pode levar alguns segundos.
            </p>
            <button 
              onClick={verificarPagamento}
              className="flex items-center justify-center gap-2 w-full bg-white/10 text-white py-4 rounded-2xl font-bold hover:bg-white/20 transition-all mb-4"
            >
              <RefreshCcw className="w-5 h-5" /> Tentar Novamente
            </button>
            <Link to="/" className="text-sm text-texto-secundario hover:text-white transition-colors">
              Voltar para a Loja e esperar
            </Link>
          </>
        )}
      </motion.div>
    </div>
  );
}
