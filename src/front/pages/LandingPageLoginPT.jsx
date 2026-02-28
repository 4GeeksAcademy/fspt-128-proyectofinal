import React, { useState } from 'react';

export const LandingPageLoginPT = () => {
  const primaryColor = "#6200e8";
  const [loading, setLoading] = useState(null);

  const handleLogin = (type) => {
    setLoading(type);
    // Simulación de navegación
    setTimeout(() => {
      console.log(`Redirigiendo a login de ${type}...`);
      setLoading(null);
    }, 1500);
  };

  return (
    <div className="container-fluid min-vh-100 d-flex align-items-center justify-content-center bg-light position-relative overflow-hidden">
      
      {/* Marca de Agua */}
      <div 
        className="position-absolute w-100 h-100 opacity-10" 
        style={{
          backgroundImage: `url('https://storage.googleapis.com/example-bucket/image_b9fda0.png')`,
          backgroundRepeat: 'no-repeat',
          backgroundPosition: 'center',
          backgroundSize: '40%',
          pointerEvents: 'none'
        }}
      />

      <main className="container position-relative z-index-1">
        <div className="row justify-content-center">
          <div className="col-11 col-md-8 col-lg-6 bg-white shadow-lg rounded-5 p-5 border text-center">
            
            <img 
              src="https://storage.googleapis.com/example-bucket/image_b9fda0.png" 
              alt="Logo" 
              className="img-fluid mb-4"
              style={{ maxWidth: "120px" }}
            />

            <h1 className="display-1 fw-bolder mb-2" style={{ color: primaryColor }}>
              VIP CC
            </h1>
            
            <p className="h5 text-muted fw-bold text-uppercase mb-5" style={{ letterSpacing: '0.3rem' }}>
              Portal Educativo
            </p>

            <div className="d-grid gap-3 d-sm-flex justify-content-sm-center">
              {/* Botón Padre */}
              <button 
                className="btn btn-lg px-5 py-3 rounded-pill fw-bold text-white shadow d-flex align-items-center justify-content-center gap-2"
                style={{ backgroundColor: primaryColor, border: 'none', minWidth: '220px' }}
                onClick={() => handleLogin('padre')}
                disabled={loading === 'padre'}
              >
                {loading === 'padre' ? (
                  <span className="spinner-border spinner-border-sm" role="status"></span>
                ) : 'Acceso Padre'}
              </button>

              {/* Botón Profesor */}
              <button 
                className="btn btn-lg px-5 py-3 rounded-pill fw-bold shadow-sm bg-transparent border-4 d-flex align-items-center justify-content-center gap-2"
                style={{ borderColor: primaryColor, color: primaryColor, minWidth: '220px' }}
                onClick={() => handleLogin('profesor')}
                disabled={loading === 'profesor'}
              >
                {loading === 'profesor' ? (
                  <span className="spinner-border spinner-border-sm" role="status"></span>
                ) : 'Acceso Profesor'}
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
