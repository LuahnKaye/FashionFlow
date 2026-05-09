import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { LayoutGrid, Download, ExternalLink, Loader2, Image as ImageIcon } from 'lucide-react';
import axios from 'axios';

export default function Galeria() {
  const [ativos, setAtivos] = useState([]);
  const [carregando, setCarregando] = useState(true);

  const API_URL = "http://localhost:8003/minha-biblioteca";

  useEffect(() => {
    const buscarAtivos = async () => {
      try {
        const token = localStorage.getItem('fashionflow_token');
        const resposta = await axios.get(API_URL, {
          headers: { Authorization: `Bearer ${token}` }
        });
        setAtivos(resposta.data);
      } catch (error) {
        console.error("Erro ao buscar biblioteca:", error);
      } finally {
        setCarregando(false);
      }
    };

    buscarAtivos();
  }, []);

  const lidarDownload = (nome) => {
    alert(`Iniciando download do ativo: ${nome}\nO arquivo .zip com os modelos 3D será baixado em instantes.`);
  };

  const lidarAbrir = (nome) => {
    alert(`Abrindo visualizador 3D para: ${nome}\nCarregando ambiente Neo-Vision...`);
  };

  const NOMES_PRODUTOS = {
    501: "Neo-Vision Ativo #501",
    502: "Cyber-Silk Ativo #502",
    503: "Ethereal Mesh #503"
  };

  const OBTER_NOME = (id) => NOMES_PRODUTOS[id] || `Asset Digital #${id}`;

  return (
    <div className="min-h-screen pt-32 px-10 pb-20">
      <div className="max-w-7xl mx-auto">
        <header className="mb-16 flex justify-between items-end">
          <div>
            <h1 className="text-sm uppercase tracking-[0.3em] text-destaque font-bold mb-4">Sua Biblioteca</h1>
            <h2 className="text-5xl font-display font-bold">Ativos Adquiridos</h2>
          </div>
          <div className="flex gap-4">
            <div className="vidro p-4 rounded-2xl flex items-center gap-3">
               <LayoutGrid className="w-5 h-5 text-texto-secundario" />
               <span className="text-sm font-bold">{ativos.length} Itens</span>
            </div>
          </div>
        </header>

        {carregando ? (
          <div className="h-64 flex items-center justify-center">
            <Loader2 className="w-10 h-10 animate-spin text-destaque" />
          </div>
        ) : ativos.length === 0 ? (
          <div className="vidro rounded-[3rem] p-20 text-center border-white/5">
            <ImageIcon className="w-20 h-20 text-white/10 mx-auto mb-6" />
            <h3 className="text-2xl font-bold mb-2">Sua galeria está vazia</h3>
            <p className="text-texto-secundario max-w-xs mx-auto">
              Adquira novos ativos na loja para que eles apareçam aqui na sua coleção exclusiva.
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {ativos.map((ativo) => (
              <motion.div 
                key={ativo.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="group relative"
              >
                <div className="aspect-square bg-segunda rounded-[2rem] overflow-hidden border border-white/10 relative">
                  <img 
                    src={ativo.url_imagem} 
                    alt={`Ativo ${ativo.id_produto}`}
                    className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-110"
                  />
                  <div className="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-4">
                    <button 
                      onClick={() => lidarDownload(OBTER_NOME(ativo.id_produto))}
                      className="bg-white text-black p-4 rounded-full hover:scale-110 transition-all shadow-xl"
                    >
                      <Download className="w-6 h-6" />
                    </button>
                    <button 
                      onClick={() => lidarAbrir(OBTER_NOME(ativo.id_produto))}
                      className="bg-white/20 backdrop-blur-md text-white p-4 rounded-full hover:scale-110 transition-all border border-white/20"
                    >
                      <ExternalLink className="w-6 h-6" />
                    </button>
                  </div>
                </div>
                <div className="mt-6 flex justify-between items-start">
                  <div>
                    <h4 className="text-xl font-bold mb-1">{OBTER_NOME(ativo.id_produto)}</h4>
                    <p className="text-xs text-texto-secundario uppercase tracking-widest">
                      Liberado em: {new Date(ativo.data_liberacao).toLocaleDateString('pt-BR')}
                    </p>
                  </div>
                  <span className="bg-green-500/10 text-green-500 text-[10px] font-black px-3 py-1 rounded-full border border-green-500/20">
                    {ativo.status}
                  </span>
                </div>
              </motion.div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
