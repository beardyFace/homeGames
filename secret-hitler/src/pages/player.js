import * as React from 'react';
import Button from '../Componants/button';

export default class Player extends React.Component {
    constructor(props) {
      super(props);
      
      this.state = {
        data:this.props.data,
        socket:this.props.socket
      };
    }
    
    componentWillReceiveProps(nextProps){
      this.setState({data: nextProps.data})
      this.setState({socket: nextProps.socket})
    }

    renderStandard(data){
      var role = data['role']

      var display = <div></div>;
      //Render role background
      if(role == 3){//hitler
        display = <img src={require('../assets//HitlerRole.PNG')} />
      }
      else if(role == 2){//facist
        display = <img src={require('../assets//FacistRole.PNG')} />
      }
      else if(role == 1){//liberal
        display = <img src={require('../assets/LiberalRole.PNG')} />  
      }
      return display  
    }

    renderSleep(data){
      var names = data['names']
      
      const listItems = names.map((player) =>
        <li key={player.toString()}>
          {player}
        </li>
      );
      return <ul>{listItems}</ul>
    }

    render() {
      const { data } = this.state;
      
      var display = this.renderStandard(data)

      var new_state = data['state']
      var state_display = <div></div>
      if(new_state == 2)//Sleep
        state_display = this.renderSleep(data)
      else if(new_state == 3)//Elect
        state_display = <div></div> 
      else if(new_state == 4)//Legislative
        state_display = <div></div> 
      else if(new_state == 5)//Executive
        state_display = <div></div> 
      else if(new_state == 6)//End
        state_display = <div></div> 

      return(
      <div>
        {display}
        {state_display}
      </div>)
    }
  }

