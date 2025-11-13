
import React from "react";
const Footer = () => {
  const year = new Date().getFullYear();
  return (
    <footer className="w-full py-6" style={{ backgroundColor: '#0b0a1d' }}>
      <div className="section-container">
        <p className="text-center text-white text-sm">© {year} Product Name. All rights reserved.</p>
      </div>
    </footer>
  );
};
export default Footer;
