import "bootstrap/dist/css/bootstrap.min.css";
import { DatePick } from "./Components/DatePick";
import { useState } from "react";
import { ButtonGroup, Container, ToggleButton } from "react-bootstrap";
import { Vis } from "./Components/Vis";
function App() {
  const [pageView, setChecked] = useState(false);
  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        justifyContent: "center",
        alignItems: "center",
        marginTop: "1rem",
      }}
    >
      <div>
        <ButtonGroup style={{ width: "10%" }}>
          <ToggleButton
            id="toggle-check-pg"
            type="checkbox"
            variant="outline-secondary"
            checked={pageView}
            onChange={(e) => setChecked(e.currentTarget.checked)}
            size="md"
          >
            Report
          </ToggleButton>
          <ToggleButton
            id="toggle-check-pg"
            type="checkbox"
            variant="outline-secondary"
            checked={!pageView}
            onChange={(e) => setChecked(!e.currentTarget.checked)}
            size="md"
          >
            Graph
          </ToggleButton>
        </ButtonGroup>
      </div>
      <hr className="my-4 w-100" />
      {pageView ? <DatePick /> : <Vis />}
    </div>
  );
}

export default App;
