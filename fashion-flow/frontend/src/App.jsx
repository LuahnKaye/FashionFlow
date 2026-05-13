import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import Hero from './components/Hero';
import Login from './pages/Login';
import Registro from './pages/Registro';
import Sucesso from './pages/Sucesso';
import Cancelado from './pages/Cancelado';
import Galeria from './pages/Galeria';
import { AuthProvider } from './context/AuthContext';
import { CartProvider } from './context/CartContext';

import { useCarrinho } from './context/CartContext';

function Home({ busca }) {
  const { adicionarAoCarrinho } = useCarrinho();
  
  const produtos = [
    { id: 501, nome: "Neo-Vision Ativo #501", preco: 0.50, categoria: "Fashion Tech", imagem: "/imagens/produto_1.png" },
    { id: 502, nome: "Cyber-Silk Ativo #502", preco: 0.50, categoria: "Digital Wear", imagem: "/imagens/produto_2.png" },
    { id: 503, nome: "Ethereal Mesh #503", preco: 0.50, categoria: "Premium Asset", imagem: "/imagens/produto_3.png" },
  ];

  const produtosFiltrados = produtos.filter(p => 
    p.nome.toLowerCase().includes(busca.toLowerCase()) || 
    p.categoria.toLowerCase().includes(busca.toLowerCase())
  );

  return (
    <>
      <Hero />
      <section id="colecoes" className="py-32 px-10 max-w-7xl mx-auto scroll-mt-20">
        <div className="flex justify-between items-end mb-16">
          <div>
            <h2 className="text-sm uppercase tracking-widest text-destaque font-bold mb-2">Curadoria</h2>
            <h3 className="text-4xl font-display font-bold">Destaques da Temporada</h3>
          </div>
          <button className="text-sm font-bold uppercase tracking-widest border-b border-white pb-2 hover:text-destaque transition-colors">
            Ver Tudo
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-10">
          {produtosFiltrados.map((produto) => (
            <div key={produto.id} className="group cursor-pointer">
              <div className="aspect-[3/4] bg-segunda overflow-hidden rounded-2xl relative mb-6 border border-white/5">
                <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center z-10">
                   <button 
                    onClick={(e) => {
                      e.stopPropagation();
                      adicionarAoCarrinho(produto);
                    }}
                    className="bg-white text-black px-6 py-3 rounded-full font-bold transform translate-y-4 group-hover:translate-y-0 transition-all duration-300 shadow-xl"
                   >
                     Adicionar
                   </button>
                </div>
                <img 
                  src={produto.imagem} 
                  alt={produto.nome} 
                  className="w-full h-full object-cover transform group-hover:scale-105 transition-transform duration-700"
                />
              </div>
              <h4 className="text-xl font-semibold mb-1">{produto.nome}</h4>
              <p className="text-texto-secundario text-sm uppercase tracking-tighter">{produto.categoria}</p>
              <div className="mt-4 font-bold text-lg text-destaque">R$ {produto.preco.toFixed(2)}</div>
            </div>
          ))}
        </div>
      </section>

      <section id="sobre" className="py-32 px-10 bg-segunda/50 backdrop-blur-sm border-t border-white/5 scroll-mt-20">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-sm uppercase tracking-[0.3em] text-destaque font-bold mb-6">Nossa Essência</h2>
          <p className="text-3xl font-display leading-relaxed mb-10">
            A FashionFlow redefine a propriedade digital, conectando a alta costura ao metaverso através de ativos 3D exclusivos e certificados.
          </p>
          <div className="flex justify-center gap-20 opacity-50 text-xs font-bold uppercase tracking-widest">
            <div>Tecnologia 3D</div>
            <div>Exclusividade</div>
            <div>Certificação</div>
          </div>
        </div>
      </section>
    </>
  );
}

function App() {
  const [termoBusca, setTermoBusca] = React.useState("");

  return (
    <AuthProvider>
      <CartProvider>
        <Router>
          <main className="min-h-screen bg-primeira text-white">
            <Navbar aoBuscar={setTermoBusca} termo={termoBusca} />
            <Routes>
              <Route path="/" element={<Home busca={termoBusca} />} />
              <Route path="/login" element={<Login />} />
              <Route path="/registrar" element={<Registro />} />
              <Route path="/sucesso" element={<Sucesso />} />
              <Route path="/cancelado" element={<Cancelado />} />
              <Route path="/galeria" element={<Galeria />} />
            </Routes>
          </main>
        </Router>
      </CartProvider>
    </AuthProvider>
  );
}

export default App;
