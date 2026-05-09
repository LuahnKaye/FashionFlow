import React, { useState } from 'react';
import { ShoppingBag, User, Search, LogOut } from 'lucide-react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useCarrinho } from '../context/CartContext';
import CartDrawer from './CartDrawer';

export default function Navbar({ aoBuscar, termo }) {
  const { usuario, logout } = useAuth();
  const { totalItens } = useCarrinho();
  const [carrinhoAberto, setCarrinhoAberto] = useState(false);
  const [pesquisando, setPesquisando] = useState(false);

  return (
    <>
      <nav className="fixed top-0 w-full z-50 py-6 px-10 flex justify-between items-center bg-black/50 backdrop-blur-md border-b border-white/5">
        <Link to="/" className="text-2xl font-black tracking-tighter font-display">
          FASHION<span className="text-destaque">FLOW</span>
        </Link>
        
        <div className="hidden md:flex gap-10 text-sm font-medium text-texto-secundario uppercase tracking-widest">
          <a href="/#colecoes" className="hover:text-white transition-colors">Coleções</a>
          <Link to="/galeria" className="hover:text-white transition-colors">Sua Galeria</Link>
          <a href="/#sobre" className="hover:text-white transition-colors">Sobre</a>
        </div>

        <div className="flex gap-6 items-center">
          <div className={`flex items-center gap-2 bg-white/5 border border-white/10 px-4 py-2 rounded-full transition-all ${pesquisando ? 'w-64' : 'w-10 overflow-hidden'}`}>
            <Search 
              className="w-4 h-4 text-texto-secundario cursor-pointer hover:text-white transition-colors flex-shrink-0" 
              onClick={() => setPesquisando(!pesquisando)}
            />
            <input 
              type="text"
              placeholder="Buscar ativos..."
              value={termo}
              onChange={(e) => aoBuscar(e.target.value)}
              className="bg-transparent border-none outline-none text-xs w-full text-white placeholder:text-white/20"
            />
          </div>
          
          {usuario ? (
            <div className="flex items-center gap-4">
              <span className="text-xs font-bold uppercase tracking-tighter text-white/70">
                Olá, {usuario.nome?.split(' ')[0] || 'Membro'}
              </span>
              <button 
                onClick={logout}
                className="p-2 hover:bg-white/10 rounded-full transition-colors text-red-400"
                title="Sair"
              >
                <LogOut className="w-5 h-5" />
              </button>
            </div>
          ) : (
            <Link to="/login" className="p-2 hover:bg-white/10 rounded-full transition-colors">
              <User className="w-5 h-5 text-texto-secundario cursor-pointer hover:text-white transition-colors" />
            </Link>
          )}

          <div 
            className="relative cursor-pointer group p-2 hover:bg-white/10 rounded-full transition-all"
            onClick={() => setCarrinhoAberto(true)}
          >
            <ShoppingBag className="w-5 h-5 text-texto-secundario group-hover:text-white transition-colors" />
            {totalItens > 0 && (
              <span className="absolute top-0 right-0 bg-white text-black text-[10px] font-bold w-4 h-4 rounded-full flex items-center justify-center animate-fade-in">
                {totalItens}
              </span>
            )}
          </div>
        </div>
      </nav>

      <CartDrawer isOpen={carrinhoAberto} onClose={() => setCarrinhoAberto(false)} />
    </>
  );
}
