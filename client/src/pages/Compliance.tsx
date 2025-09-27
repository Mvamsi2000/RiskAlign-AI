import { cisControls } from "../data/controls";

function Compliance() {
  return (
    <div>
      <h1>Compliance Overview</h1>
      <p>
        Track how organizational controls map to the CIS framework and quickly
        identify owners and coverage.
      </p>
      <table>
        <thead>
          <tr>
            <th scope="col">Control</th>
            <th scope="col">Description</th>
            <th scope="col">Category</th>
          </tr>
        </thead>
        <tbody>
          {cisControls.map((control) => (
            <tr key={control.id}>
              <td>{control.id}</td>
              <td>{control.description}</td>
              <td>{control.category}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default Compliance;
