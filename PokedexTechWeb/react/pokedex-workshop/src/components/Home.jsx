import React, { useState, useRef } from 'react';
import { motion } from "framer-motion"
import Col from 'react-bootstrap/Col';
import Row from 'react-bootstrap/Row';

import pokemon from'../assets/pokemon.png';
import pokemonLogo from'../assets/pokemon-logo.png';
import lusofona from'../assets/universidade-lusofona.png';
import logoCGI from'../assets/CGI_logo.png';
import pokeball from'../assets/pokeball.png';
import '../App.css';

import { useFollowPointer } from "../typescript/use-follow-pointer.ts"

const Home = () => {
    const [shouldAnimate, setShouldAnimate] = useState(false); // adiciona estado para controlar animação
    const animation = {
        scale: 1.1, // aumenta a escala do componente em 10%
        rotate: [0, -10, 10, -10, -20, 20, -20, -30, 30, -30, 0], // valores de rotação para a animação
        transition: { duration: 1.0 } // duração da animação
    };

    const handleClick = () => {
        setShouldAnimate(!shouldAnimate); // atualiza o estado para parar a animação
    };

    const ref = useRef(null);
    const { x, y } = useFollowPointer(ref);

    return (
        <div>
            <Row>
                <Col>
                    <a href="https://www.ulusofona.pt/" target="_blank" rel="noreferrer">
                        <img 
                            src={lusofona} 
                            alt="Universidade Lusofona" 
                            width="500"
                        />
                    </a>
                    <a href="https://www.cgi.com/portugal/pt-pt" target="_blank" rel="noreferrer">
                        <img 
                        src={logoCGI} 
                        alt="CGI" 
                        width="80"/>
                    </a>
                </Col>
            </Row>
            <Row>
                <Col>
                <motion.img
                    whileHover={animation} 
                    src={pokemonLogo} 
                    alt="Pokemon logo" 
                    width="500" 
                    style={{ marginTop: '50px' }}
                />
                </Col>
            </Row>
            <Row>
                <Col>
                    <img src={pokemon} alt="Pokemon Management" width="500" style={{ marginLeft: '50px', marginTop: '50px' }}/>
                </Col>
            </Row>

            <Row>
                <Col>
                    <motion.img
                    ref={ref}
                    whileHover={{ scale: 1.2 }}
                    animate={shouldAnimate ? { x, y } : undefined}
                    transition={{
                        type: "spring",
                        damping: 5,
                        stiffness: 150,
                        restDelta: 0.001
                    }}
                    src={pokeball}
                    className="Pokeball"
                    onClick={handleClick}
                    style={{ marginTop: '50px' }}
                    />
                </Col>
            </Row>
        </div>
    );
}
 
export default Home;