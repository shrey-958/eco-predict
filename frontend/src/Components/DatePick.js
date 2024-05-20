import DatePicker from "react-datepicker";
import { Button, ButtonGroup, Form, ToggleButton } from "react-bootstrap";
import "react-datepicker/dist/react-datepicker.css";
import { useState } from "react";

export const DatePick = () => {
  const [startDate, setStartDate] = useState(new Date("11/01/2020"));
  const [checked, setChecked] = useState(false);
  const [reportContent, setReportContent] = useState("The report will be generated here");

  const onSubmit = async (e) => {
    try {
      setReportContent("Loading....");
      const currentDate = startDate;
      const year = startDate.getFullYear();
      const month = startDate.getMonth() + 1; // Months are zero-based
      const day = startDate.getDate();
      const hours = startDate.getHours();
      let url;
      if (checked) {
        url = `http://127.0.0.1:5000/?date=${year}-${month}-${day}&hour=${hours}`;
      } else {
        url = `http://127.0.0.1:5000/?date=${year}-${month}-${day}&?hour=-1}`;
      }
      const data = await fetch(url);
      const response = await data.json();
      setReportContent(response.llm_response);
      // You can also handle the llm_response if needed
    } catch {
      setReportContent("Error");
    }
  };

  console.log(startDate);

  return (
    <div>
      <div
        style={{
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          marginTop: "2rem",
        }}
      >
        <div style={{ marginRight: "16px" }}>
          <DatePicker
            showTimeSelect={checked}
            minDate={new Date("11/01/2020")} // 1 jan
            maxDate={new Date("12/16/2020")} // dec 16
            selected={startDate}
            onChange={(date) => setStartDate(date)}
            timeIntervals={60}
          />
        </div>
        <ButtonGroup style={{ width: "100%" }}>
          <ToggleButton
            id="toggle-check"
            type="checkbox"
            variant="outline-primary"
            checked={checked}
            onChange={(e) => setChecked(e.currentTarget.checked)}
            size="sm"
          >
            Hour
          </ToggleButton>
          <ToggleButton
            id="toggle-check"
            type="checkbox"
            variant="outline-primary"
            checked={!checked}
            onChange={(e) => setChecked(!e.currentTarget.checked)}
            size="sm"
          >
            Day
          </ToggleButton>
        </ButtonGroup>
      </div>

      <Form.Control
        as="textarea"
        placeholder="Leave a comment here"
        value={reportContent}
        style={{ height: "600px", width: "600px", marginTop: "10px" }}
        disabled
      />

      <div
        style={{ display: "flex", justifyContent: "center", marginTop: "16px" }}
      >
        <Button size="md" onClick={onSubmit}>
          Generate Report
        </Button>
      </div>
    </div>
  );
};
