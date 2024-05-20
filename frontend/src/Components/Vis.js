import { useState } from "react";
import { Carousel, Form, Button } from "react-bootstrap";

export const Vis = () => {
  const images = [
    "https://imgtr.ee/images/2024/05/02/41a3d1e31e7476604b0a7ddd9845853c.png",
    "https://imgtr.ee/images/2024/05/02/e5800448e773c6a0ab4b96a22df3e5e4.png",
    "https://imgtr.ee/images/2024/05/02/c0f385e13fd45276070e6ce52944e7b6.png",
    "https://imgtr.ee/images/2024/05/02/3d54f155ce9320fb63caf43448402724.png",
  ];
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("The answer will be generated here");
  const onSubmit = async (image) => {
    try {
      setAnswer("Loading...");
      const url = "http://127.0.0.1:5000/langchain"; // Corrected URL
      const data = await fetch(url, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ image_url: image, user_question: question }), // Corrected JSON payload
      });
      const response = await data.json();
      setAnswer(response.result); // Assuming the response contains a "result" key
    } catch (err) {
      console.log(err);
      setAnswer("Error");
    }
  };
  return (
    <div>
      <Carousel slide={false} style={{ height: "400px" }} interval={null}>
        {images.map((image) => (
          <Carousel.Item key={image}>
            <div style={{ marginRight: "1.7rem" }}>
              <img
                className="d-block w-100"
                src={image}
                alt="First slide"
                style={{
                  objectFit: "cover",
                  height: "400px",
                  width: "400px",
                }}
              />
            </div>
            <Form.Control
              type="text"
              placeholder="Ask your question"
              value={question}
              onChange={(event) => setQuestion(event.target.value)}
              className="mt-3"
            />
            <Form.Control
              as="textarea"
              placeholder="Leave a comment here"
              value={answer}
              style={{ height: "200px", marginTop: "10px" }}
              disabled
            />
            <div
              style={{
                display: "flex",
                justifyContent: "center",
                marginTop: "16px",
              }}
            >
              <Button onClick={() => onSubmit(image)}>Ask Question</Button>
            </div>
          </Carousel.Item>
        ))}
        {/* <div>Ask Question</div> */}
      </Carousel>
    </div>
  );
};
