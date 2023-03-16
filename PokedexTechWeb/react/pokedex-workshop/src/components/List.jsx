import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import Table from "react-bootstrap/Table";
import Col from "react-bootstrap/Col";
import Row from "react-bootstrap/Row";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faPencil, faTrash } from "@fortawesome/free-solid-svg-icons";
import { motion } from "framer-motion";

import Pokemons from "../assets/fourPokemons.png";
import "../App.css";
import Modal from "./Modal";

const List = () => {
  const navigate = useNavigate();
  const [pokemonList, setPokemonList] = useState([]);
  const [pokemonToDelete, setPokemonToDelete] = useState("");
  const hoverAnimation = {
    scale: 1.1, // aumenta a escala do componente em 10%
    transition: { duration: 0.5 }, // duração da animação
  };
  const tapAnimation = {
    scale: 0.9, // diminui a escala do componente em 10%
    transition: { duration: 0.2 }, // duração da animação
  };

  useEffect(() => {
    getPokemonList();
  }, []);

  const getPokemonList = () => {
    const url = "https://a22003179-pokemonapi.azurewebsites.net/api/pokedex";

    fetch(url)
      .then((result) => result.json())
      .then((result) => {
        setPokemonList(result);
      });
  };

  const handleEdit = (pokemon) => {
    navigate("/edit", { state: pokemon });
  };

  const handleDelete = () => {
    const url = `https://a22003179-pokemonapi.azurewebsites.net/api/pokedex/${pokemonToDelete}`;
    fetch(url, {
      method: "DELETE",
      headers: { "Content-Type": "application/json" },
    })
      .then((result) => {
        if (result.status === 200) {
          getPokemonList();
        } else {
          alert("Error deleting pokemon, try again");
        }
      })
      .finally(() => {
        setPokemonToDelete("");
      });
  };

  const tableRows = pokemonList.map((entry, index) => {
    const {
      PokemonName,
      PokemonNumber,
      PokemonColor,
      PokemonType,
      PokemonAttacks,
    } = entry;
    return (
      <tr key={index}>
        <td>{PokemonName}</td>
        <td>{PokemonNumber}</td>
        <td>{PokemonColor}</td>
        <td>{PokemonType}</td>
        <td
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-evenly",
          }}
        >
          <Col
            md="auto"
            onClick={() =>
              handleEdit({
                name: PokemonName,
                pokemonNumber: PokemonNumber,
                pokemonColor: PokemonColor,
                pokemonType: PokemonType,
                pokemonAttacks: PokemonAttacks,
              })
            }
          >
            <FontAwesomeIcon style={{ textAlign: "center" }} icon={faPencil} />
          </Col>
          <Col md="auto" onClick={() => setPokemonToDelete(PokemonName)}>
            <FontAwesomeIcon style={{ textAlign: "center" }} icon={faTrash} />
          </Col>
        </td>
      </tr>
    );
  });

  return (
    <>
      <h1 className="page-title">Pokémon List</h1>
      <Table className="press-start-table" striped bordered hover>
        <TableHeader />
        <tbody>{tableRows}</tbody>
      </Table>
      <Modal
        isOpen={!!pokemonToDelete}
        onClose={() => setPokemonToDelete("")}
        onSubmit={handleDelete}
        modalHeading="Are you sure you want to delete this pokemon?"
        modalBody={pokemonToDelete}
        onCloseText="Cancel"
        onSubmitText="Delete"
      />

      {tableRows.length > 0 && (
        <Row>
          <Col>
            <motion.img
              whileHover={hoverAnimation}
              whileTap={tapAnimation}
              src={Pokemons}
              alt="Pokemons"
              className="Pokemons"
            />
          </Col>
        </Row>
      )}
    </>
  );
};

const TableHeader = () => {
  return (
    <thead>
      <tr>
        <th>Pokemon Name</th>
        <th>Pokemon Number</th>
        <th>Pokemon Color</th>
        <th>Pokemon Type</th>
        <th>Actions</th>
      </tr>
    </thead>
  );
};

export default List;
