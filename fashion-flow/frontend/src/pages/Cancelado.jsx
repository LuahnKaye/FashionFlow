import React from 'react';
import { motion } from 'framer-motion';
import { XCircle, ShoppingBag, AlertCircle } from 'lucide-react';
import { Link } from 'react-router-dom';

export default function Cancelado() {
  return (
    <div className="min-h-screen flex items-center justify-center px-4 pt-20">
      <div className="absolute top-0 left-0 w-full h-full -z-10 bg-[radial-gradient(circle_at_50%_50%,#1a0a0a_0%,#000000_100%)]" />
      
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="vidro w-full max-w-lg p-12 rounded-[3rem] shadow-2xl text-center border-red-500/20"
      >
        <div className="w-20 h-20 bg-red-500/20 rounded-full flex items-center justify-center mx-auto mb-8">
          <XCircle className="w-10 h-10 text-red-500" />
        </div>

        <h1 className="text-3xl font-display font-bold mb-4">Pagamento Cancelado</h1>
        <p className="text-texto-secundario mb-10">
          Não se preocupe, nenhuma cobrança foi realizada. Seus itens continuam seguros no seu carrinho.
        </p>

        <div className="flex flex-col gap-3">
          <Link 
            to="/" 
            className="flex items-center justify-center gap-2 bg-white text-black py-4 rounded-2xl font-bold hover:scale-[1.02] transition-all"
          >
            Tentar Novamente <ShoppingBag className="w-5 h-5" />
          </Link>
          <div className="flex items-center justify-center gap-2 text-texto-secundario text-sm py-2">
            <AlertCircle className="w-4 h-4" />
            <span>Precisa de ajuda? Entre em contato.</span>
          </div>
        </div>
      </motion.div>
    </div>
  );
}
