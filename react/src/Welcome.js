import React from "react";
import "./Welcome.css"
import logo from "./welcome.png"

export default class Header extends React.Component{
  render() {
    return (
      <div className="component-welcome">
        <img src={logo}/>
      </div>
    );
  }

}