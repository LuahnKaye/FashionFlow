import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Mail, Lock, ArrowRight, Loader2, AlertCircle } from 'lucide-react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function Login() {
  const [email, setEmail] = useState('');
  const [senha, setSenha] = useState('');
  const [carregando, setCarregando] = useState(false);
  const [erro, setErro] = useState('');
  
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    setCarregando(true);
    setErro('');

    const resultado = await login(email, senha);
    
    if (resultado.sucesso) {
      navigate('/'); // Redireciona para a home após o login
    } else {
      setErro(resultado.erro);
    }
    setCarregando(false);
  };

  return (
    <div className="min-h-screen flex items-center justify-center px-4 relative">
      <div className="absolute top-0 left-0 w-full h-full -z-10 bg-[radial-gradient(circle_at_50%_50%,#1a1a1a_0%,#000000_100%)]" />
      
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="vidro w-full max-w-md p-10 rounded-[2rem] shadow-2xl"
      >
        <div className="text-center mb-10">
          <h2 className="text-3xl font-display font-bold mb-2">Bem-vindo de volta</h2>
          <p className="text-texto-secundario">Acesse sua conta para gerenciar seus ativos.</p>
        </div>

        {erro && (
          <motion.div 
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            className="bg-red-500/10 border border-red-500/20 text-red-500 p-4 rounded-xl mb-6 flex items-center gap-3 text-sm"
          >
            <AlertCircle className="w-5 h-5 flex-shrink-0" />
            {erro}
          </motion.div>
        )}

        <form className="space-y-6" onSubmit={handleLogin}>
          <div className="space-y-2">
            <label className="text-sm font-semibold ml-1 text-texto-secundario uppercase tracking-widest">E-mail</label>
            <div className="relative group">
              <Mail className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-texto-secundario group-focus-within:text-white transition-colors" />
              <input 
                type="email" 
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="seu@email.com"
                className="w-full bg-white/5 border border-white/10 rounded-2xl py-4 pl-12 pr-4 outline-none focus:border-white/30 focus:bg-white/10 transition-all text-white"
              />
            </div>
          </div>

          <div className="space-y-2">
            <label className="text-sm font-semibold ml-1 text-texto-secundario uppercase tracking-widest">Senha</label>
            <div className="relative group">
              <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-texto-secundario group-focus-within:text-white transition-colors" />
              <input 
                type="password" 
                required
                value={senha}
                onChange={(e) => setSenha(e.target.value)}
                placeholder="••••••••"
                className="w-full bg-white/5 border border-white/10 rounded-2xl py-4 pl-12 pr-4 outline-none focus:border-white/30 focus:bg-white/10 transition-all text-white"
              />
            </div>
          </div>

          <button 
            type="submit"
            disabled={carregando}
            className="w-full bg-white text-black py-4 rounded-2xl font-bold flex items-center justify-center gap-2 hover:scale-[1.02] active:scale-[0.98] disabled:opacity-50 disabled:hover:scale-100 transition-all mt-10"
          >
            {carregando ? (
              <>Processando <Loader2 className="w-5 h-5 animate-spin" /></>
            ) : (
              <>Entrar <ArrowRight className="w-5 h-5" /></>
            )}
          </button>
        </form>

        <div className="mt-8 text-center text-sm">
          <span className="text-texto-secundario">Ainda não tem uma conta? </span>
          <Link to="/registrar" className="text-white font-bold hover:underline">Cadastre-se</Link>
        </div>
      </motion.div>
    </div>
  );
}
