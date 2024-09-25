import React from "react";
import { Link } from "react-router-dom";

const Header = ({ isAltHeader, toggleMenu }) => (
  <header id="header" className={isAltHeader ? "alt" : "reveal"}>
    <h1>
      <Link to="/">AutoAngle</Link>
    </h1>
    <a href="#menu" onClick={toggleMenu}>Menu</a>
  </header>
);

export default Header;
