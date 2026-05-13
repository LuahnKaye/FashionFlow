import React from 'react';
import { motion } from 'framer-motion';
import { ArrowRight } from 'lucide-react';

export default function Hero() {
  return (
    <section className="relative h-screen w-full flex flex-col items-center justify-center overflow-hidden pt-20">
      {/* Elemento Decorativo de Fundo */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-blue-600/10 blur-[150px] rounded-full -z-10" />
      
      <div className="text-center max-w-4xl px-4">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
        >
          <h2 className="text-sm uppercase tracking-[0.5em] text-texto-secundario mb-6 font-semibold">
            Redefinindo o Digital Fashion
          </h2>
          <h1 className="text-6xl md:text-8xl font-black mb-8 leading-[1.1] font-display tracking-tight gradiente-texto">
            A ERA DOS <br /> ATIVOS DIGITAIS
          </h1>
        </motion.div>

        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.4, duration: 1 }}
          className="text-lg md:text-xl text-texto-secundario mb-12 max-w-2xl mx-auto font-light leading-relaxed"
        >
          Explore coleções exclusivas de ativos digitais e peças premium. 
          Onde a tecnologia Saga encontra a alta costura em um fluxo resiliente.
        </motion.p>

        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.6 }}
          className="flex flex-col sm:flex-row gap-6 justify-center"
        >
          <button className="bg-white text-black px-10 py-5 rounded-full font-bold hover:scale-105 transition-transform flex items-center justify-center gap-2 group">
            Ver Coleções <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
          </button>
          <button className="vidro px-10 py-5 rounded-full font-semibold hover:bg-white/10 transition-all">
            Como Funciona
          </button>
        </motion.div>
      </div>

      {/* Indicador de Scroll */}
      <motion.div 
        animate={{ y: [0, 10, 0] }}
        transition={{ repeat: Infinity, duration: 2 }}
        className="absolute bottom-10 w-6 h-10 border-2 border-white/20 rounded-full flex justify-center p-1"
      >
        <div className="w-1 h-2 bg-white/50 rounded-full" />
      </motion.div>
    </section>
  );
}
