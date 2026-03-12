import React from 'react';
import { useNavigate } from 'react-router-dom';

export const LandingPagePT = () => {
  const primaryColor = "#6200e8";
  const navigate = useNavigate();

  return (
    <div className="container-fluid min-vh-100 d-flex align-items-center justify-content-center bg-light">
      
      <main className="container">
        <div className="row justify-content-center">
          <div className="col-11 col-md-8 col-lg-6 bg-white shadow-lg rounded-5 p-4 p-md-5 border text-center">
            
          

            <h1 className="display-1 fw-bolder mb-2" style={{ color: primaryColor }}>
              VIP CC
            </h1>
            
            <p className="h5 text-muted fw-bold text-uppercase mb-5" style={{ letterSpacing: '0.3rem' }}>
              Portal Educativo
            </p>

            <div className="d-grid gap-3 d-sm-flex justify-content-sm-center">
              
            
              <button 
                className="btn btn-lg px-5 py-3 rounded-pill fw-bold text-white shadow"
                style={{ backgroundColor: primaryColor, border: 'none', minWidth: '220px' }}
                onClick={() => navigate('/')} 
              >
                Acceso Tutor Legal
              </button>

             
              <button 
                className="btn btn-lg px-5 py-3 rounded-pill fw-bold shadow-sm bg-transparent border-4"
                style={{ borderColor: primaryColor, color: primaryColor, minWidth: '220px' }}
                onClick={() => navigate('/')} 
              >
                Acceso Profesor
              </button>
            </div>

            <footer className="mt-5 pt-4 text-secondary small opacity-50 border-top">
              © 2026 VIP CC • Transformando la educación
            </footer>

          </div>
        </div>
      </main>
    </div>
  );
}