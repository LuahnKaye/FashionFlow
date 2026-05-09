import React, { createContext, useState, useContext, useEffect } from 'react';
import axios from 'axios';
import { jwtDecode } from 'jwt-decode';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [usuario, setUsuario] = useState(null);
  const [carregando, setCarregando] = useState(true);

  // URL do nosso Servico de Identidade (FastAPI) na porta 8004
  const API_URL = "http://localhost:8000";

  useEffect(() => {
    // Ao carregar o app, verifica se ja existe um token salvo
    const token = localStorage.getItem('fashionflow_token');
    if (token) {
      try {
        const dados = jwtDecode(token);
        setUsuario({ ...dados, token });
      } catch (error) {
        localStorage.removeItem('fashionflow_token');
      }
    }
    setCarregando(false);
  }, []);

  const login = async (email, senha) => {
    try {
      // O seu backend espera JSON puro com email e senha
      const resposta = await axios.post(`${API_URL}/login`, {
        email,
        senha
      });
      const token = resposta.data.token_acesso;

      localStorage.setItem('fashionflow_token', token);
      const dados = jwtDecode(token);
      setUsuario({ ...dados, token });
      
      return { sucesso: true };
    } catch (error) {
      console.error("Erro no login:", error);
      return { 
        sucesso: false, 
        erro: error.response?.data?.detail || "Falha na conexão com o servidor." 
      };
    }
  };

  const registrar = async (nome, email, senha) => {
    try {
      // Alterado de /usuarios/ para /registro conforme rotas_autenticacao.py
      const resposta = await axios.post(`${API_URL}/registro`, {
        nome,
        email,
        senha
      });
      return { sucesso: true, dados: resposta.data };
    } catch (error) {
      console.error("Erro no registro:", error);
      return { 
        sucesso: false, 
        erro: error.response?.data?.detail || "Erro ao criar conta. Tente outro e-mail." 
      };
    }
  };

  const logout = () => {
    localStorage.removeItem('fashionflow_token');
    setUsuario(null);
  };

  return (
    <AuthContext.Provider value={{ usuario, login, registrar, logout, carregando }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
