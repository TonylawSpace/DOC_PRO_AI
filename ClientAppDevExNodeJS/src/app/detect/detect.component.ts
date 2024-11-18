import { Component } from '@angular/core';
import { HttpClient } from '@angular/common/http';

@Component({
  selector: 'app-detect',
  templateUrl: './detect.component.html',
  styleUrls: ['./detect.component.css']
})
export class DetectComponent {
  constructor(private http: HttpClient) {}
  response: any;  // 定義 response 變量來存儲服務器返回的結果

  onFileSelected(event: any) {
    const file: File = event.target.files[0];
    if (file) {
      const formData = new FormData();
      formData.append('file', file, file.name);

      this.http.post('http://192.168.0.73:5600/detect', formData).subscribe(
        (res: any) => {
          this.response = res;
          console.log('Response:', res); 
        },
        (error) => {
          console.error('Error:', error);
        }
      );
    }
  }
}
