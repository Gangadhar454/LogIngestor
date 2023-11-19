import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup } from '@angular/forms';
import { HttpClient } from "@angular/common/http";
import { Observable } from 'rxjs';
import { DatePipe } from '@angular/common';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent {
  title = 'Log-Ingestor';
  myForm!: FormGroup;
  keys: string[] = [
    "level",
    "message",
    "resourceId",
    "timestamp",
    "traceId",
    "spanId",
    "commit",
    "metadata"
  ]
  private apiBaseUrl = 'http://localhost:3000';
  response : any;

  constructor(private fb: FormBuilder,public http: HttpClient, private datePipe: DatePipe) {
    this.createForm();
  }

  createForm() {
    this.myForm = this.fb.group({
      key : '',
      logicalCondition: '',
      searchValue : '',
      timestampRange: '',
      metaData: 'parentResourceId'
    })
  }

  onKeyChange() {
    if(this.myForm.value.key == 'timestamp') {
      this.myForm.controls['logicalCondition'].setValue('range');
      this.myForm.controls['logicalCondition'].disable();
    }
    else {
      this.myForm.controls['logicalCondition'].setValue('');
      this.myForm.controls['logicalCondition'].enable();      
    }
  }

  doFilter() {
    console.log(this.myForm.value);
    let payload = {
      key : this.myForm.value.key != 'metadata' ?  this.myForm.value.key : this.myForm.value.key + '.parentResourceId',
      operation : this.myForm.value.key != 'timestamp' ? this.myForm.value.logicalCondition : 'range',
      value : this.myForm.value.key != 'timestamp' ? this.myForm.value.searchValue : {lower_range : this.formateDate(this.myForm.value.timestampRange?.[0]), upper_range : this.formateDate(this.myForm.value.timestampRange?.[1])}
    };
    this.callFilterApi(payload).subscribe((res) => {
      this.response = res?.results;
    })
  }

  formateDate(date: string) {
    return new Date(date).toISOString().replace(/.\d+Z$/g, "Z");
  }

  callFilterApi(payload : any) :Observable<any> {
    return this.http.post<any>(this.apiBaseUrl + "/logs/filter/",payload)
  }

}
