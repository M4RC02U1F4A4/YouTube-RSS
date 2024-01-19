import React, { useState, useEffect } from "react";
import { Input, Navbar, NavbarBrand, NavbarContent, NavbarItem, Link, NavbarMenuToggle, NavbarMenu, NavbarMenuItem, Modal, ModalContent, ModalHeader, ModalBody, ModalFooter, Button, useDisclosure } from "@nextui-org/react";
import { useDataContext } from '../context/Data';
import Channel from './Channel';
import config from '../config';

export default function NavBar({ activePage, handleNavLinkClick }) {

  const [windowWidth, setWindowWidth] = useState(window.innerWidth);
  const {isOpen, onOpen, onOpenChange} = useDisclosure();
  const [searchTerm, setSearchTerm] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const {channelsData} = useDataContext();

  const handleSearch = async () => {
    try {
      const response = await fetch(`${config.API_BASE_URL}/search/${searchTerm}`);
      const data = await response.json();
      if (data.data && data.data.items && data.data.items.length > 0) {
        setSearchResults(data.data.items);
      } else {
        setSearchResults([]);
      }
      console.log(data);
    } catch (error) {
      console.error('Errore nella richiesta:', error);
    }
  };

  const handleKeyPress = (event) => {
    if (event.key === 'Enter') {
      handleSearch();
    }
  };


  useEffect(() => {
    const handleResize = () => {
      setWindowWidth(window.innerWidth);
    };

    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
    };
  }, []);

  const isSmallScreen = windowWidth < 640;

  return (
    <>
      {isSmallScreen ? (
        <SmallScreenNavbar activePage={activePage} handleNavLinkClick={handleNavLinkClick} onOpen={onOpen} />
      ) : (
        <LargeScreenNavbar activePage={activePage} handleNavLinkClick={handleNavLinkClick} onOpen={onOpen}/>
      )}
      <Modal isOpen={isOpen} scrollBehavior='inside' onOpenChange={onOpenChange} size="4xl" className="dark text-foreground bg-background" backdrop="blur" hideCloseButton>
        <ModalContent>
          {(onClose) => (
            <>
              <ModalHeader className="flex flex-col gap-1">Manage - Add new channel</ModalHeader>
              <ModalBody>
                <div className="flex items-center">
                  <Input className="flex-1" type="text" value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} onKeyDown={(e) => handleKeyPress(e)} label="Query" />  
                  <Button className="antialiased font-semibold ml-4 h-full py-4 px-4" color="primary" variant="ghost" onClick={handleSearch}> Search </Button>
                </div>
                <div className="channel-grid">
                  {searchResults.map((channel, index) => (
                      <Channel key={index}
                          avatarSrc={channel.snippet.thumbnails.default.url}
                          channelName={channel.snippet.channelTitle}
                          channelDescription={channel.snippet.description}
                          channelID={channel.id.channelId}
                          action={channelsData[channel.id.channelId] ? "remove" : "add"}
                          stats="false"
                      />
                  ))}
                </div>
                
              </ModalBody>
              <ModalFooter>
              </ModalFooter>
            </>
          )}
        </ModalContent>
      </Modal>
    </>
  );

}

const SmallScreenNavbar = ({ activePage, handleNavLinkClick, onOpen }) => {

  const [isMenuOpen, setIsMenuOpen] = React.useState(false)

  const handleMenuItemClick = (page) => {
    setIsMenuOpen(false);
    handleNavLinkClick(page);
  };

  return (
    <Navbar isBordered isMenuOpen={isMenuOpen} onMenuOpenChange={setIsMenuOpen} >
      <NavbarContent className="sm:hidden" justify="start">
        <NavbarMenuToggle aria-label={isMenuOpen ? "Close menu" : "Open menu"} />
      </NavbarContent>

      <NavbarContent className="sm:hidden pr-3" justify="center">
        <NavbarBrand>
          <a className="font-bold text-inherit" href="/" >YouTube RSS</a>
        </NavbarBrand>
      </NavbarContent>

      <NavbarContent justify="end">
        <NavbarItem>
          <Button className="antialiased font-semibold" color="primary" variant="ghost" onPress={onOpen}>
            Manage
          </Button>
        </NavbarItem>
      </NavbarContent>

      <NavbarMenu className="dark text-foreground bg-background">
          <NavbarMenuItem>
            <Link className="cursor-pointer" color={activePage === "home" ? "primary" : "foreground"} onClick={() => handleMenuItemClick("home")}>
              Home
            </Link>
          </NavbarMenuItem>
          <NavbarMenuItem>
            <Link className="cursor-pointer" color={activePage === "channels" ? "primary" : "foreground"} onClick={() => handleMenuItemClick("channels")}>
            Channels
            </Link>
          </NavbarMenuItem>
          <NavbarMenuItem>
            <Link className="cursor-pointer" color={activePage === "videos" ? "primary" : "foreground"} onClick={() => handleMenuItemClick("videos")}>
              Videos
            </Link>
          </NavbarMenuItem>
      </NavbarMenu>
    </Navbar>
  );
};

const LargeScreenNavbar = ({ activePage, handleNavLinkClick, onOpen }) => {
  return (
    <Navbar>
      <NavbarBrand>
        <a className="font-bold text-inherit" href="/" >YouTube RSS</a>
      </NavbarBrand>
      <NavbarContent className="sm:flex gap-4" justify="center">
        <NavbarItem isActive={activePage === "home"}>
          <Link className="cursor-pointer" color={activePage === "home" ? "primary" : "foreground"} onClick={() => handleNavLinkClick("home")}>
            Home
          </Link>
        </NavbarItem>
        <NavbarItem isActive={activePage === "channels"}>
          <Link className="cursor-pointer" color={activePage === "channels" ? "primary" : "foreground"} onClick={() => handleNavLinkClick("channels")}>
            Channels
          </Link>
        </NavbarItem>
        <NavbarItem isActive={activePage === "videos"}>
          <Link className="cursor-pointer" color={activePage === "videos" ? "primary" : "foreground"} onClick={() => handleNavLinkClick("videos")}>
            Videos
          </Link>
        </NavbarItem>
      </NavbarContent>
      <NavbarContent justify="end">
        <NavbarItem>
          <Button className="antialiased font-semibold" color="primary" variant="ghost" onPress={onOpen}>
            Manage
          </Button>
        </NavbarItem>
      </NavbarContent>
    </Navbar>
  );
};