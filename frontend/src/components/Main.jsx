import React, { useState, useEffect } from 'react';
import NavBar from './NavBar';
import Home from './HomePage'
import Videos from './VideosPage'
import Channels from './ChannelsPage'

const Main = () => {

  const [activePage, setActivePage] = useState(localStorage.getItem('activePage') || 'home');

  useEffect(() => {
    localStorage.setItem('activePage', activePage);
  }, [activePage]);

  const handleNavLinkClick = (page) => {
    setActivePage(page);
  };

  return (
    <div className='mx-8'>
        <NavBar activePage={activePage} handleNavLinkClick={handleNavLinkClick} />
        <div>
            {activePage === "home" && <Home />}
            {activePage === "channels" && <Channels />}
            {activePage === "videos" && <Videos />}
        </div>
    </div>
  );
};

export default Main;



              