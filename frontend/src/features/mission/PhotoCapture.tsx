import { useRef, useState } from "react";
import "./PhotoCapture.css";

interface PhotoCaptureProps {
  onCapture: (dataUrl: string) => void;
}

export function PhotoCapture({ onCapture }: PhotoCaptureProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [preview, setPreview] = useState<string | null>(null);

  const handleFile = (file: File) => {
    const reader = new FileReader();
    reader.onload = () => {
      const dataUrl = reader.result as string;
      setPreview(dataUrl);
      onCapture(dataUrl);
    };
    reader.readAsDataURL(file);
  };

  return (
    <div className="photo-capture">
      {preview ? (
        <img className="photo-capture__preview" src={preview} alt="Фото миссии" />
      ) : (
        <button className="photo-capture__button" onClick={() => inputRef.current?.click()}>
          📷 Сделать фото
        </button>
      )}
      {preview && (
        <button
          className="photo-capture__retake"
          onClick={() => {
            setPreview(null);
            if (inputRef.current) inputRef.current.value = "";
          }}
        >
          Переснять
        </button>
      )}
      <input
        ref={inputRef}
        type="file"
        accept="image/*"
        capture="environment"
        className="photo-capture__input"
        onChange={(e) => {
          const file = e.target.files?.[0];
          if (file) handleFile(file);
        }}
      />
    </div>
  );
}
