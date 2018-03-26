import * as React from 'react';
import Button from '../Componants/button';

export default class Join extends React.Component {
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

    render() {
      const { data } = this.state;
      //Start game button if is host
      //Display who is in the lobby
      // return <div>{this.state.data}</div>
      // return <div>{this.state.data['name']}</div>

      return (
        <div>
            <label>
                Name:            
                <input value={this.state.name} onChange={(evt) => { this.setState({name:evt.target.value}) }}/> 
            </label>

            <Button caption="Join" onclick={() => {(
                this.state.socket.emit('join', {'name':this.state.name})
            )}}/>
        </div>
      );
    }
  }

