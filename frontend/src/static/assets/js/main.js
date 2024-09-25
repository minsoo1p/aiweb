import React, { useEffect, useState } from 'react';
import "./static/assets/css/main.css";

const App = () => {
  const [isPreload, setIsPreload] = useState(true);
  const [isAltHeader, setIsAltHeader] = useState(true);
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  // Breakpoints
  const breakpoints = {
    xlarge: [1281, 1680],
    large: [981, 1280],
    medium: [737, 980],
    small: [481, 736],
    xsmall: [0, 480],
  };

  useEffect(() => {
    // Remove preload class after load
    window.setTimeout(() => {
      setIsPreload(false);
    }, 100);

    // Scroll event for header
    const handleScroll = () => {
      const header = document.getElementById('header');
      const banner = document.getElementById('banner');
      if (banner) {
        const headerHeight = header.offsetHeight;
        const bannerBottom = banner.getBoundingClientRect().bottom;

        if (bannerBottom < headerHeight) {
          setIsAltHeader(false);
        } else {
          setIsAltHeader(true);
        }
      }
    };

    window.addEventListener('scroll', handleScroll);

    // Clean up event listener on component unmount
    return () => {
      window.removeEventListener('scroll', handleScroll);
    };
  }, []);

  // Menu toggle
  const toggleMenu = () => {
    setIsMenuOpen((prev) => !prev);
  };

  return (
    <div className={isPreload ? 'is-preload' : ''}>
      {/* Header */}
      <header id="header" className={isAltHeader ? 'alt' : 'reveal'}>
        <h1>Header</h1>
      </header>

      {/* Banner */}
      <section id="banner">
        <h2>Banner</h2>
      </section>

      {/* Menu */}
      <div id="menu" className={isMenuOpen ? 'open' : ''}>
        <a href="#menu" className="close" onClick={toggleMenu}>
          Close
        </a>
        <nav>
          <ul>
            <li><a href="#home">Home</a></li>
            <li><a href="#about">About</a></li>
            <li><a href="#contact">Contact</a></li>
          </ul>
        </nav>
      </div>

      {/* Main content */}
      <div className="content">
        <p>Main content goes here.</p>
      </div>

      {/* Menu toggle button */}
      <button className="menu-toggle" onClick={toggleMenu}>
        {isMenuOpen ? 'Close Menu' : 'Open Menu'}
      </button>
    </div>
  );
};

export default App;
