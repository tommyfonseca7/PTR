import React, { useState, useEffect, useRef } from "react";
import { motion } from "framer-motion";

import pikachuRunner from "../assets/pikachuRunner.gif";

const About = () => {
  const [positionX, setPositionX] = useState(0);
  const [animationStarted, setAnimationStarted] = useState(true);
  const parentRef = useRef();

  useEffect(() => {
    if (animationStarted) {
      const imageWidth = 120;
      const parentWidth = parentRef.current.offsetWidth;
      const maxPositionX = parentWidth - imageWidth;

      const handleAnimationFrame = () => {
        setPositionX((prevPositionX) =>
          prevPositionX >= maxPositionX ? 0 : prevPositionX + 1
        );
        requestAnimationFrame(handleAnimationFrame);
      };

      requestAnimationFrame(handleAnimationFrame);

      return () => {
        cancelAnimationFrame(handleAnimationFrame);
      };
    }
  }, [animationStarted]);

  return (
    <>
      <div className="about-container">
        <div className="about-page">
          <h1 className="page-title">About PokéManager</h1>
          <p className="about-content">
            With the help of our app, you can create your custom pokémon in just
            a few steps. You can choose the type of pokémon, select special
            abilities, customize colors, name, and much more.
          </p>
          <p className="about-content">
            Our team of experts work tirelessly to provide you with the best
            experience possible.
          </p>
          <p className="about-content">
            Our app offers a wide range of customization options, allowing you
            to create a pokémon that is officially unique. You can adjust your
            Pokémon's appearance, choose its type, define its strengths and
            weaknesses, and even create a story unique to it.
          </p>
          <p className="about-content">
            Furthermore, our Pokémon breeding app is easy to use and offers an
            intuitive interface. Even if you're a beginner, you'll be able to
            create your own unique Pokémon without any difficulties. With our
            app, creating your custom Pokémon is a fun and easy task.
          </p>
          <p className="about-content">
            So, if you're a Pokémon fan who's always dreamed of creating your
            own unique character, access our Pokémon Breeding app now. With it,
            you can bring your imagination to life and create the Pokémon of
            your dreams!
          </p>
        </div>
      </div>
      <div className="center-image" ref={parentRef}>
        <motion.img
          className="pikachuRunner"
          src={pikachuRunner}
          alt="Running"
          width="120"
          height="auto"
          initial={{ x: positionX }}
          animate={{ x: positionX }}
          transition={{
            type: "tween",
            velocity: 1,
            duration: 0,
          }}
        />
      </div>
    </>
  );
};

export default About;
