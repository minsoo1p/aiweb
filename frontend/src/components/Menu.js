import React from 'react';

const Menu = ({ isMenuOpen, toggleMenu, currentUser }) => {

  const handleClose = () => {
    // 메뉴를 닫고 해시를 URL에서 제거
    toggleMenu();  // 메뉴 열림/닫힘을 처리
    
    if (window.location.hash) {
      window.history.replaceState(null, null, window.location.pathname + window.location.search);
    }
  };

  return (
    <nav id="menu" className={isMenuOpen ? 'visible' : ''}>
      <a href="#" className="close" onClick={handleClose}>
        Close
      </a>
      <ul className="links">
        <li><a href="/">Home</a></li>
        <li><a href="/info">Usage Information</a></li>
        <li><a href="/article">Related Article</a></li>
        {currentUser?.isAuthenticated && (
          <li><a href="/project">{currentUser.name}'s Projects</a></li>
        )}
      </ul>

      <ul className="actions stacked">
        {currentUser?.isAuthenticated ? (
          <li><a href="/logout" className="button primary fit">Logout</a></li>
        ) : (
          <>
            <li><a href="/register" className="button primary fit">Sign Up</a></li>
            <li><a href="/login" className="button fit">Log In</a></li>
          </>
        )}
      </ul>
    </nav>
  );
};

export default Menu;
