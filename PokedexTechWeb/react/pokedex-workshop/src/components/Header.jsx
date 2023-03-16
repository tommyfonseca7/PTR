import React from 'react';
import Container from 'react-bootstrap/Container';
import Nav from 'react-bootstrap/Nav';
import Navbar from 'react-bootstrap/Navbar';
import { Link, useLocation } from "react-router-dom";
import { motion } from "framer-motion";
import pokeballIcon from '../assets/small-pokeball-icon.jpg';
import '../App.css';

function Header() {
  const location = useLocation();

  const SlowFastSlow = () => {
    const animation = {
      rotate: [0, 180, 360],
      scale: 1.2,
      transition: {
        duration: 0.5,
        ease: "easeInOut",
        times: [0, 0.25, 0.5],
      },
    };

    return (
      <motion.img
        whileHover={animation}
        whileTap={{ scale: 1.4 }}
        src={pokeballIcon}
        width="70"
        className="d-inline-block align-top"
        alt="React Bootstrap logo"
      />
    );
  };

  return (
    <>
      <Navbar variant="dark" className="navbar-custom">
        <Container className="justify-content-center">
          <Nav className="mx-auto justify-content-between">
            <Nav.Link exact as={Link} to="/">
              <SlowFastSlow />
            </Nav.Link>
            <Nav.Link
              as={Link}
              to="/list"
              className={location.pathname === '/list' ? 'active' : ''}
            >
              Pokémon List
            </Nav.Link>
            <Nav.Link
              as={Link}
              to="/create"
              className={location.pathname === '/create' ? 'active' : ''}
            >
              New Pokémon
            </Nav.Link>
            <Nav.Link
              as={Link}
              to="/about"
              className={location.pathname === '/about' ? 'active' : ''}
            >
              About PokéManager
            </Nav.Link>
          </Nav>
        </Container>
      </Navbar>
    </>
  );
}

export default Header;
