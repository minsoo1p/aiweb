import React, { useState, useEffect } from 'react';
import './App.css';

// NavList Component
const NavList = ({ items }) => {
  const renderNavList = (items, indent = 0) => {
    return items.map((item, index) => (
      <a
        key={index}
        href={item.href}
        target={item.target || '_self'}
        className={`link depth-${indent}`}
      >
        <span className={`indent-${indent}`}></span>
        {item.text}
      </a>
    ));
  };

  return <div>{renderNavList(items)}</div>;
};

// Panel Component
const Panel = ({ children, side = 'right', visibleClass = 'visible', hideOnEscape = true }) => {
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    const handleKeyDown = (event) => {
      if (hideOnEscape && event.keyCode === 27) {
        setIsVisible(false);
      }
    };

    if (isVisible) {
      window.addEventListener('keydown', handleKeyDown);
    }

    return () => {
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, [isVisible, hideOnEscape]);

  const togglePanel = () => setIsVisible(!isVisible);

  return (
    <div>
      <button onClick={togglePanel}>Toggle Panel</button>
      <div className={`panel ${isVisible ? visibleClass : ''} ${side}`}>
        {children}
        <button onClick={() => setIsVisible(false)}>Close Panel</button>
      </div>
    </div>
  );
};

// Placeholder Component
const PlaceholderInput = ({ type, placeholder }) => {
  const [value, setValue] = useState('');

  return (
    <input
      type={type}
      value={value}
      placeholder={placeholder}
      onChange={(e) => setValue(e.target.value)}
      onFocus={() => setValue('')}
      onBlur={() => {
        if (value === '') setValue(placeholder);
      }}
    />
  );
};

// Prioritize Component
const Prioritize = ({ elements, condition }) => {
  const prioritizedElements = condition
    ? [...elements].sort((a, b) => a.priority - b.priority)
    : elements;

  return (
    <div>
      {prioritizedElements.map((element, index) => (
        <div key={index}>{element.content}</div>
      ))}
    </div>
  );
};

// Example App Component
const App = () => {
  const navItems = [
    { href: '#home', text: 'Home' },
    { href: '#about', text: 'About' },
    { href: '#contact', text: 'Contact' },
  ];

  const elements = [
    { content: 'Element 1', priority: 2 },
    { content: 'Element 2', priority: 1 },
  ];

  return (
    <div className="App">
      <NavList items={navItems} />
      <Panel side="left">
        <p>This is a panel content.</p>
      </Panel>
      <PlaceholderInput type="text" placeholder="Enter your name" />
      <Prioritize elements={elements} condition={true} />
    </div>
  );
};

export default App;
