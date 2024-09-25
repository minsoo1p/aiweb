import React, { useEffect, useState } from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import "./static/assets/css/main.css";
import Header from "./components/Header";
import Menu from "./components/Menu";
import Footer from "./components/Footer";
import Home from "./Home";  
import Info from "./information";  
import Article from "./article";  
import Project from "./project";  
import Login from "./login";  
import Register from "./register";
import { getBreakpoint } from "./utils/breakpoints";  

const App = ({ currentUser }) => {
  const [isPreload, setIsPreload] = useState(true);
  const [isAltHeader, setIsAltHeader] = useState(true);
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [currentBreakpoint, setCurrentBreakpoint] = useState(getBreakpoint());

  useEffect(() => {
    window.setTimeout(() => {
      setIsPreload(false);
    }, 100);

    const handleScroll = () => {
      const header = document.getElementById("header");
      const banner = document.getElementById("banner");
      if (banner) {
        const headerHeight = header.offsetHeight;
        const bannerBottom = banner.getBoundingClientRect().bottom;
        setIsAltHeader(bannerBottom >= headerHeight);
      }
    };

    const handleResize = () => {
      setCurrentBreakpoint(getBreakpoint());
    };

    // Handle hash change to open/close the menu
    const handleHashChange = () => {
      if (window.location.hash === "#menu") {
        setIsMenuOpen(true);  // Open the menu if URL contains #menu
      } else {
        setIsMenuOpen(false);  // Close the menu otherwise
      }
    };

    window.addEventListener("scroll", handleScroll);
    window.addEventListener("resize", handleResize);
    window.addEventListener("hashchange", handleHashChange);  // Listen for hash changes

    // Check the current URL hash when the component mounts
    handleHashChange();

    return () => {
      window.removeEventListener("scroll", handleScroll);
      window.removeEventListener("resize", handleResize);
      window.removeEventListener("hashchange", handleHashChange);
    };
  }, []);

  const toggleMenu = () => {
    // If the menu is currently open, close it and update the URL hash
    if (isMenuOpen) {
      window.history.pushState("", document.title, window.location.pathname + window.location.search);
    } else {
      window.location.hash = "#menu";  // Add #menu to the URL to open the menu
    }
    setIsMenuOpen((prev) => !prev);
  };

  return (
    <div className={isPreload ? "is-preload" : ""}>

        <Header isAltHeader={isAltHeader} toggleMenu={toggleMenu} />
        <Menu isMenuOpen={isMenuOpen} toggleMenu={toggleMenu} currentUser={currentUser} />

        {/* Routes */}
        <Routes>
          <Route path="/" element={<Home currentUser={currentUser} />} />
          <Route path="/info" element={<Info />} />
          <Route path="/article" element={<Article />} />
          <Route path="/project" element={<Project />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
        </Routes>

        <Footer />

    </div>
  );
};

export default App;
